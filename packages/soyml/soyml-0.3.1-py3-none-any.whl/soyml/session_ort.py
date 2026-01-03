import os
import time
import atexit
from typing import Callable, List, Optional
import onnxruntime as ort


def select_best_providers(blacklist: Optional[List[str]] = None):
    all_providers = ort.get_available_providers()
    accel_providers = [
        "CUDAExecutionProvider",
        "MIGraphXExecutionProvider",
        "ROCMExecutionProvider",
        "CoreMLExecutionProvider",
        "DirectMLExecutionProvider",
        "CPUExecutionProvider",
    ]

    if blacklist:
        accel_providers = [p for p in accel_providers if p not in blacklist]

    provider = next((p for p in accel_providers if p in all_providers), None)
    return [provider] if provider else ["CPUExecutionProvider"]


def _env_truthy(name: str) -> bool:
    value = os.getenv(name)
    return value is not None and str(value).lower() not in ("0", "false", "no", "off")


def _sanitize_profile_label(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in value)


def _get_profile_prefix(model_name: Optional[str] = None) -> Optional[str]:
    if not _env_truthy("SOYML_ORT_PROFILE"):
        return None
    prefix = os.getenv("SOYML_ORT_PROFILE_PREFIX")
    if prefix:
        base_dir = os.path.dirname(prefix)
        base_name = os.path.basename(prefix)
        if model_name:
            base_name = f"{base_name}_{_sanitize_profile_label(model_name)}"
        return os.path.join(base_dir, base_name) if base_dir else base_name

    out_dir = os.getenv("SOYML_ORT_PROFILE_DIR", ".")
    ts = time.strftime("%Y%m%d_%H%M%S")
    base_name = f"ort_profile_{ts}_{os.getpid()}_{time.time_ns()}"
    if model_name:
        base_name = f"{base_name}_{_sanitize_profile_label(model_name)}"
    return os.path.join(out_dir, base_name)


def _configure_session_options(
    log,
    model_name: Optional[str] = None,
) -> tuple[ort.SessionOptions, Optional[Callable[[ort.InferenceSession], None]]]:
    session_options = ort.SessionOptions()
    profile_prefix = _get_profile_prefix(model_name)
    if not profile_prefix:
        return session_options, None

    profile_dir = os.path.dirname(profile_prefix)
    if profile_dir:
        os.makedirs(profile_dir, exist_ok=True)
    session_options.enable_profiling = True
    session_options.profile_file_prefix = profile_prefix

    def _flush_profile(session: ort.InferenceSession) -> None:
        try:
            profile_path = session.end_profiling()
            log.info(f"ort profile written to: {profile_path}")
        except Exception as exc:
            log.warn(f"ort profile flush failed: {exc}")

    return session_options, _flush_profile


def session_ort_init(
    self,
    use_cpu_only: bool = False,
    provider_blacklist: Optional[List[str]] = None,
):
    log = self.log.logger_for("session_ort")
    model_name = None
    if getattr(self, "ort_model_file", None):
        model_name = os.path.splitext(os.path.basename(self.ort_model_file))[0]
    session_options, flush_profile = _configure_session_options(log, model_name)
    blacklist = []
    if provider_blacklist:
        blacklist.extend(provider_blacklist)
    providers = (
        ["CPUExecutionProvider"]
        if use_cpu_only
        else select_best_providers(blacklist=blacklist)
    )

    try:
        log.debug(f"creating ort inference session with providers: {providers}")
        self.ort_session = ort.InferenceSession(
            self.ort_model_file,
            session_options,
            providers=providers,
        )
        self.inputs = self.ort_session.get_inputs()
        self.outputs = self.ort_session.get_outputs()
        self.input_shapes = {item.name: item.shape for item in self.inputs}
        self.output_shapes = {item.name: item.shape for item in self.outputs}

        inputs_str = [
            f"{item.name}@{item.type}{item.shape}" for item in self.inputs
        ]
        outputs_str = [
            f"{item.name}@{item.type}{item.shape}" for item in self.outputs
        ]
        log.debug(f"  ort session inputs: {inputs_str}")
        log.debug(f"  ort session outputs: {outputs_str}")

        if flush_profile:
            atexit.register(flush_profile, self.ort_session)

    except Exception as e:
        raise Exception(f"failed to load ort model: {e}")


def session_ort_execute(self, inputs, output_names):
    try:
        outputs = self.ort_session.run(output_names, inputs)
    except Exception as e:
        raise Exception(f"failed to execute ort: {e}")

    return outputs
