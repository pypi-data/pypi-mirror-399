from enum import Enum


class PackageSearchGrepRequestRegistry(str, Enum):
    CRATES_IO = "crates_io"
    GOLANG_PROXY = "golang_proxy"
    NPM = "npm"
    PY_PI = "py_pi"

    def __str__(self) -> str:
        return str(self.value)
