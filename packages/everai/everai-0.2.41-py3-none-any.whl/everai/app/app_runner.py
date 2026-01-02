import threading

from everai.app.app_setup import AppSetupMixin, _AppSetupFunction
from everai.app.context import service_context, Context
import typing

from everai.app.service import Service
from everai.app.app_runtime import AppRuntime


class AppRunnerMixin(AppSetupMixin):
    _service: typing.Optional[Service] = None
    _runtime: AppRuntime
    lock: threading.Lock

    def do_prepare(self):
        self._do_setup_funcs('prepare', self._prepare_funcs)

    def do_clear(self):
        self._do_setup_funcs('clear', self._clear_funcs)

    @property
    def runtime(self) -> AppRuntime:
        return self._runtime

    @runtime.setter
    def runtime(self, runtime: AppRuntime):
        self._runtime = runtime
        self.service.runtime = runtime

    def _do_setup_funcs(self,
                        func_type: typing.Literal['prepare', 'clear'],
                        funcs: typing.List[_AppSetupFunction],
                        ):
        for func in funcs or []:
            try:
                print(f'staring {func_type} func {func.name}')
                with service_context(self.runtime.context()):
                    func()

                print(f'{func_type} func {func.name} successfully finished')
            except Exception as e:
                print(f'{func_type} func {func.name} failed with {e}')
                if not func.optional:
                    raise e
                else:
                    continue

    @property
    def ctx(self):
        return self.runtime.context()
        # return Context(secrets=self.prepared_secrets, volumes=self.prepared_volumes)

    @property
    def service(self):
        if self._service is None:
            self._service = Service()
        return self._service
