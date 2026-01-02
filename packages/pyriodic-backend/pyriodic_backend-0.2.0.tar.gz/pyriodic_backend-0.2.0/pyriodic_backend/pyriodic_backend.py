import logging
from typing import Callable

from bs4 import BeautifulSoup

from .backend import FileJSONBackend
from .entities import HTMLFile, RegisteredMethod
from .protocols import BackendProtocol

logger = logging.getLogger(__name__)


class PyriodicBackend:
    def __init__(
        self,
        backend: BackendProtocol = FileJSONBackend(),
        allow_partial: bool = False,
    ):
        self.allow_partial = allow_partial
        self.backend: BackendProtocol = backend
        self.registered_methods: list[RegisteredMethod] = []

    def register(
        self, html_file: HTMLFile, tag_id: str, func: Callable, interval: int = 1
    ) -> RegisteredMethod:
        new_method = RegisteredMethod(
            html_file=html_file, tag_id=tag_id, func=func, interval=interval
        )
        self.registered_methods.append(new_method)
        return new_method

    def run(self):
        logger.debug("Run start")
        application_matrix = {}
        # first step:
        # Decide which methods need to run and group them by file
        for registered_method in self.registered_methods:
            logger.debug(
                f"Initializing method {registered_method.func.__name__} on tag {registered_method.tag_id}"
            )
            minutes_since_last_run = self.backend.get_minutes_since_last_run(
                registered_method
            )
            if (
                minutes_since_last_run is not None
                and minutes_since_last_run < registered_method.interval
            ):
                logger.debug("Skipping method execution, time not yet passed")
                continue

            # start grouping methods by file to switch the data structure for
            # the second step
            if registered_method.html_file.abs_file_path not in application_matrix:
                application_matrix[registered_method.html_file.abs_file_path] = []

            application_matrix[registered_method.html_file.abs_file_path].append(
                registered_method
            )
        # Second step:
        # update files with the registered methods

        # below we are using the switched the data structure, the application
        # matrix is a dict with keys being the file paths, and their values
        # being the list of methods to run on that file, this way we only need
        # to open and save each file once per the whole execution cycle of PB

        for abs_file_path in application_matrix:
            self._update_file(
                abs_file_path=abs_file_path, methods=application_matrix[abs_file_path]
            )

    def _update_file(self, abs_file_path: str, methods: list[RegisteredMethod]):
        soup = self._load_html_file(abs_file_path)
        if not soup:
            return
        for registered_method in methods:
            try:
                tag = soup.find(id=registered_method.tag_id)
                if tag:
                    tag.string = registered_method.func()  # type: ignore
                else:
                    logger.warning(f"tag {registered_method.tag_id} not found")
                    continue
            except Exception:
                logger.exception(
                    f"An exception occured when running method {registered_method.func.__name__} to change tag id {registered_method.tag_id} "
                )
                if not self.allow_partial:
                    break
            else:
                logger.debug(f"Method {registered_method.func.__name__} executed")
                self.backend.record(registered_method)
        else:
            # only if the inner loop finishes without breaks, do save the file
            self._save_html_file(abs_file_path, soup)

    def _load_html_file(self, abs_file_path: str) -> BeautifulSoup | None:
        try:
            with open(abs_file_path, "r") as input_html_file:
                return BeautifulSoup(input_html_file, "html.parser")
        except FileNotFoundError:
            logger.error(
                f"File {abs_file_path} could not be opened. Is the absolute path correct?"
            )
            return None

    def _save_html_file(self, abs_file_path: str, soup: BeautifulSoup):
        try:
            with open(abs_file_path, "w") as output_html_file:
                output_html_file.write(str(soup))
        except PermissionError:
            logger.exception(
                f"Could not save file {abs_file_path}, insufficient permissions?"
            )
        else:
            logger.debug(f"file {abs_file_path} update finished")
