import time

from lldb import *

from lldbvis.events import signals
from lldbvis.events import dispatcher
from lldbvis.meta import Singleton
from lldbvis.util import bpl
from lldbvis.util.log import LogLevel


class Debugger:
    __metaclass__ = Singleton

    def __init__(self):
        self.debugger = SBDebugger.Create()
        assert self.debugger.IsValid()
        self.target = SBTarget()
        self.process = SBProcess()
        self.listener = self.debugger.GetListener()

        self.running = False
        self.paused = False
        self.isSetup = False

        self._log_queue = []

    def consume_log(self):
        log_item = self._log_queue.pop(0)
        return log_item

    def is_log_empty(self):
        return len(self._log_queue) == 0

    @dispatcher.send(signal=signals.LogDebugger)
    def append_log(self, msg, log_level=LogLevel.INFO):
        log_item = (msg, log_level)
        self._log_queue.append(log_item)

    def get_arch(self):
        return self.debugger.GetSelectedTarget().triple.split('-')[0]

    def is_i386(self):
        if self.get_arch()[:1] == 'i':
            return True
        return False

    def is_x64(self):
        arch = self.get_arch()
        if arch == 'x86_64' or arch == 'x86_64h':
            return True
        return False

    def is_arm(self):
        if 'arm' in self.get_arch():
            return True
        return False

    def resume(self):
        if self.running and self.paused:
            self.paused = False
            self.process.Continue()

    def stop(self):
        if self.running and not self.paused:
            self.paused = True
            self.process.Stop()

    def kill(self):
        if self.running:
            self.paused = False
            self.process.Kill()
            self.finish()

    def step_out(self):
        if self.running and self.paused:
            self.paused = False
            cur_thread = self.get_selected_thread()
            cur_thread.StepOut()

    def step_into(self):
        if self.running and self.paused:
            self.paused = False
            cur_thread = self.get_selected_thread()
            cur_thread.StepInto()

    def step_over(self):
        if self.running and self.paused:
            self.paused = False
            cur_thread = self.get_selected_thread()
            cur_thread.StepOver()

    def step_instruction(self):
        if self.running and self.paused:
            self.paused = False
            cur_thread = self.get_selected_thread()
            cur_thread.StepInstruction(True)

    def step_out_of_frame(self):
        if self.running and self.paused:
            self.paused = False
            cur_thread = self.get_selected_thread()
            cur_thread.StepOutOfFrame(self.get_selected_frame())

    @dispatcher.send(signal=signals.EndDebugger)
    def finish(self):
        self.running = False

    def _setupBreakpoints(self):
        bpl.read()
        files = bpl.get_files()
        for file in files:
            name = file["name"]
            bps = file["breakpoints"]
            for bp in bps:
                self.target.BreakpointCreateByLocation(str(name), int(bp) + 1)

    @dispatcher.send(signal=signals.SetupDebugger)
    def setup(self, dir, targetFile):
        self.paused = False

        self.target = self.debugger.CreateTarget(dir + targetFile)
        if not self.target.IsValid():
            raise ValueError('Could not create target')

        self._setupBreakpoints()

        args = [dir + targetFile]
        launch_info = SBLaunchInfo(args)
        launch_info.SetWorkingDirectory(dir)
        launch_info.SetLaunchFlags(eLaunchFlagNone)

        error = SBError()
        self.process = self.target.Launch(launch_info, error)
        if not error.Success() or not self.process.IsValid():
            raise ValueError('Could not launch process')
        else:
            self.isSetup = True

    def threads(self):
        res = []
        for i in range(self.process.GetNumThreads()):
            res.append(self.process.GetThreadAtIndex(i))
        return res

    def frames(self, thread=None):
        res = []
        if thread is None:
            for t in self.threads():
                for i in range(t.GetNumFrames()):
                    res.append(t.GetFrameAtIndex(i))
        else:
            for i in range(thread.GetNumFrames()):
                res.append(thread.GetFrameAtIndex(i))
        return res

    def values(self, frame=None, thread=None):
        res = []
        if frame is None:
            for f in self.frames(thread):
                values = SBValueList(f.GetVariables(True, True, False, True))
                for i in range(values.GetSize()):
                    res.append(values.GetValueAtIndex(i))
        else:
            values = SBValueList(frame.GetVariables(True, True, False, True))
            for i in range(values.GetSize()):
                res.append(values.GetValueAtIndex(i))
        return res

    def thread(self, id):
        return self.process.GetThreadByID(id)

    def frame(self, id, thread=None):
        if thread is not None:
            for i in range(thread.GetNumFrames()):
                f = SBFrame(thread.GetFrameAtIndex(i))
                if f.GetFrameID() == id:
                    return f
        else:
            for t in self.threads():
                for i in range(t.GetNumFrames()):
                    f = SBFrame(t.GetFrameAtIndex(i))
                    if f.GetFrameID() == id:
                        return f
        return None

    def value(self, id, frame=None, thread=None):
        if frame is None:
            for f in self.frames(thread):
                values = SBValueList(f.GetVariables(True, True, False, True))
                for i in range(values.GetSize()):
                    val = SBValue(values.GetValueAtIndex(i))
                    if val.GetID() == id:
                        return val
        else:
            values = SBValueList(frame.GetVariables(True, True, False, True))
            for i in range(values.GetSize()):
                val = SBValue(values.GetValueAtIndex(i))
                if val.GetID() == id:
                    return val

    def value_children(self, value, allow_pointers=True, allow_arrays=True, allow_refs=True, allow_type_defs=True,
                       allow_functions=True, type_complete=True):
        child_values = []

        if value.MightHaveChildren():
            for i in range(value.GetNumChildren()):
                child_value = value.GetChildAtIndex(i)

                if child_value.IsValid():
                    child_type = child_value.GetType()

                    if child_type.IsTypeComplete() or not type_complete:

                        if child_type.IsPointerType():
                            if allow_pointers:
                                child_values.append(child_value)

                        elif child_type.IsArrayType():
                            if allow_arrays:
                                child_values.append(child_value)

                        elif child_type.IsReferenceType():
                            if allow_refs:
                                child_values.append(child_value)

                        elif child_type.IsTypedefType():
                            if allow_type_defs:
                                child_values.append(child_value)

                        elif child_type.IsFunctionType():
                            if allow_functions:
                                child_values.append(child_value)

                        else:
                            child_values.append(child_value)

        return child_values

    def get_selected_thread(self):
        return self.process.GetSelectedThread()

    def get_selected_frame(self):
        return self.get_selected_thread().GetSelectedFrame()

    def get_selected_frame_file(self):
        file_spec = SBFileSpec(self.get_selected_frame().GetLineEntry().GetFileSpec())
        if file_spec.GetDirectory() is None or file_spec.GetFilename() is None:
            return None
        return str(file_spec.GetDirectory()) + '/' + str(file_spec.GetFilename())

    def execute_command(self, cmd):
        ci = self.debugger.GetCommandInterpreter()
        execution_result = SBCommandReturnObject()
        ci.HandleCommand(cmd, execution_result)
        return execution_result

    def add_breakpoint(self, file, line):
        self.target.BreakpointCreateByLocation(file, line)

    def remove_breakpoint(self, bp):
        self.target.BreakpointDelete(bp.GetID())

    def get_breakpoints(self, file=None, line=None):
        if file is None:
            if self.target is None:
                return []
            bps = []
            for i in range(self.target.GetNumBreakpoints()):
                bps.append(self.target.GetBreakpointAtIndex(i))
            return bps
        else:
            bps = self.get_breakpoints()
            res = []
            for bp in bps:
                line_entry = SBLineEntry(bp.GetLocationAtIndex(0).GetAddress().GetLineEntry())
                file_spec = SBFileSpec(line_entry.GetFileSpec())
                if file == str(file_spec.GetDirectory()) + '/' + str(file_spec.GetFilename()):
                    if line is not None:
                        if line_entry.GetLine() == line:
                            res.append(bp)
                    else:
                        res.append(bp)
            return res

    @dispatcher.send(signal=signals.PauseDebugger)
    def pause(self):
        self.paused = True

    def _wait_while_paused(self, timeout=-1):
        if timeout > 0:
            end_time = time.time() + timeout
            while time.time() < end_time:
                if not self.paused:
                    return True
                time.sleep(0.2)
            return False
        else:
            while self.paused:
                time.sleep(0.2)
            return True

    @dispatcher.send(signal=signals.StartDebugger, when=dispatcher.Before)
    def start(self):
        event = SBEvent()
        self.running = True
        while self.running:
            self._wait_while_paused()

            if self.process.GetState() == eStateExited:
                break

            if self.listener.WaitForEvent(5, event):
                if not event.IsValid():
                    break

                if not SBProcess.EventIsProcessEvent(event):
                    continue

                event_type = event.GetType()

                if event_type == SBProcess.eBroadcastBitStateChanged:
                    state = SBProcess.GetStateFromEvent(event)

                    if state == eStateStopped:
                        self.pause()

                    else:
                        continue

                elif event_type == SBProcess.eBroadcastBitSTDOUT:
                    while True:
                        output = self.process.GetSTDOUT(1024)
                        if output:
                            self.append_log(output)
                        else:
                            break

                elif event_type == SBProcess.eBroadcastBitSTDERR:
                    while True:
                        output = self.process.GetSTDERR(1024)
                        if output:
                            self.append_log(output, LogLevel.ERROR)
                        else:
                            break

                elif event_type == SBProcess.eBroadcastBitInterrupt:
                    print 'Interrupted'  # TODO: what situations would give rise to this event - STDIN

            else:
                break

        self.finish()


if debugger:
    del debugger

debugger = Debugger()
