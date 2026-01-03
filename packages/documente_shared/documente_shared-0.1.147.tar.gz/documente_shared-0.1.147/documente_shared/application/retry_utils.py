import time
import random
from functools import wraps
from typing import Optional, Callable
from loguru import logger


def retry_on_size_integrity(base_delay: float = 0.8, max_retries: int = 3):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, file_key: str, *args, **kwargs) -> Optional[dict]:
            for attempt in range(max_retries):
                try:
                    file_context = func(self, file_key, *args, **kwargs)

                    if not file_context:
                        logger.warning(
                            f"[Intento {attempt+1}/{max_retries}] file_context es None para {file_key}"
                        )
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                            time.sleep(delay)
                            continue
                        raise RuntimeError(f"No se pudo obtener file_context para {file_key}")

                    if 'Body' not in file_context:
                        logger.warning(
                            f"[Intento {attempt+1}/{max_retries}] 'Body' no encontrado en file_context para {file_key}"
                        )
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                            time.sleep(delay)
                            continue
                        raise RuntimeError(f"'Body' no encontrado en file_context para {file_key}")

                    expected_size = file_context.get('ContentLength', 0)
                    body = file_context['Body'].read()
                    actual_size = len(body)

                    if expected_size == actual_size:
                        file_context['Body'] = body
                        if attempt > 0:
                            logger.info(f"Descarga exitosa de {file_key} después de {attempt+1} intentos")
                        return file_context

                    logger.warning(
                        f"[Intento {attempt+1}/{max_retries}] Discrepancia de tamaño para {file_key}: "
                        f"esperado={expected_size}, recibido={actual_size}"
                    )

                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                        time.sleep(delay)

                except Exception as e:
                    logger.error(
                        f"[Intento {attempt+1}/{max_retries}] Error al descargar {file_key}: {type(e).__name__}: {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                        time.sleep(delay)
                        continue
                    raise

            raise RuntimeError(
                f"Descarga incompleta/inconsistente de S3 para {file_key} después de {max_retries} intentos"
            )
        return wrapper
    return decorator
