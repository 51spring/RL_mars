from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
from mars_env.native_lifecycle import close_native_client


class NativeLifecycleTests(unittest.TestCase):
    def modules(self,parent,wait):
        no_such=type('NoSuchProcess',(Exception,),{})
        return {'psutil':SimpleNamespace(Process=Mock(return_value=parent),NoSuchProcess=no_such,
                                        wait_procs=Mock(side_effect=wait)),
                'zmq':SimpleNamespace(LINGER=17)}

    def test_only_owned_tree_is_terminated_and_stubborn_children_killed(self):
        parent,child=Mock(),Mock();parent.children.return_value=[child]
        native=SimpleNamespace(_client_process_pid=123,_server=Mock())
        modules=self.modules(parent,[([child],[parent]),([parent],[])])
        with patch.dict('sys.modules',modules):close_native_client(native)
        modules['psutil'].Process.assert_called_once_with(123)
        parent.terminate.assert_called_once();child.terminate.assert_called_once()
        parent.kill.assert_called_once();child.kill.assert_not_called()
        self.assertIsNone(native._client_process_pid)
        native._server.setsockopt.assert_called_once_with(17,0)

    def test_repeated_close_with_no_client_does_not_launch_or_signal_any_process(self):
        native=SimpleNamespace(_client_process_pid=None,_server=None)
        modules=self.modules(Mock(),[([],[]),([],[])])
        with patch.dict('sys.modules',modules):close_native_client(native)
        modules['psutil'].Process.assert_not_called()
        self.assertTrue(native._last_is_send)

    def test_failed_cleanup_keeps_pid_for_followup_and_invalid_pid_refused(self):
        parent=Mock();parent.children.return_value=[]
        native=SimpleNamespace(_client_process_pid=123,_server=None)
        modules=self.modules(parent,[([],[parent]),([],[parent])])
        with patch.dict('sys.modules',modules):
            with self.assertRaises(RuntimeError):close_native_client(native)
        self.assertEqual(native._client_process_pid,123)
        with patch.dict('sys.modules',modules):
            with self.assertRaises(ValueError):close_native_client(SimpleNamespace(_client_process_pid=0))


if __name__=='__main__':unittest.main()
