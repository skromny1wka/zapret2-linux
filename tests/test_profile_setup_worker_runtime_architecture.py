from __future__ import annotations

import inspect
import unittest


class ProfileSetupWorkerRuntimeArchitectureTests(unittest.TestCase):
    def test_profile_setup_list_file_workers_start_through_runtime(self) -> None:
        from profile.ui.profile_setup_page import ProfileSetupPageBase

        init_source = inspect.getsource(ProfileSetupPageBase.__init__)
        payload_source = inspect.getsource(ProfileSetupPageBase._request_profile_setup_payload)
        list_load_source = inspect.getsource(ProfileSetupPageBase._request_list_file_editor_state)
        validation_request_source = inspect.getsource(ProfileSetupPageBase._request_list_file_validation)
        validation_start_source = inspect.getsource(ProfileSetupPageBase._start_list_file_validation_worker)
        save_request_source = inspect.getsource(ProfileSetupPageBase._request_list_file_save)
        save_start_source = inspect.getsource(ProfileSetupPageBase._start_list_file_save_worker)
        cleanup_source = inspect.getsource(ProfileSetupPageBase.cleanup)

        expected_runtimes = (
            "_setup_load_runtime",
            "_list_file_load_runtime",
            "_list_file_validation_runtime",
            "_list_file_save_runtime",
        )
        for attr in expected_runtimes:
            self.assertIn(f"{attr} = OneShotWorkerRuntime()", init_source)
            self.assertIn(attr, cleanup_source)

        for attr, source in (
            ("_setup_load_runtime", payload_source),
            ("_list_file_load_runtime", list_load_source),
            ("_list_file_validation_runtime", validation_request_source + validation_start_source),
            ("_list_file_save_runtime", save_request_source + save_start_source),
        ):
            self.assertIn(f'_worker_runtime("{attr}")', source)
            self.assertIn("start_qthread_worker", source)
            self.assertNotIn("worker.start()", source)

        for old_attr in (
            "self._setup_load_worker",
            "self._list_file_load_worker",
            "self._list_file_validation_worker",
            "self._list_file_save_worker",
        ):
            self.assertNotIn(old_attr, init_source)


if __name__ == "__main__":
    unittest.main()
