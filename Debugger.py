from lldb import *

from Metaclasses import Singleton
from Observer import observable


class Debugger:
    __metaclass__ = Singleton

    def __init__(self):
        self.debugger = SBDebugger(SBDebugger.Create())
        assert self.debugger.IsValid()
        self.target = SBTarget()
        self.process = SBProcess()
        self.listener = SBListener(self.debugger.GetListener())
        self.isSetup = False

    @observable
    def setup(self, dir, targetFile):
        self.target = SBTarget(self.debugger.CreateTarget(dir + targetFile))
        if not self.target.IsValid():
            raise ValueError

        self.target.BreakpointCreateByName('main')

        args = [dir + targetFile]
        launch_info = SBLaunchInfo(args)
        launch_info.SetWorkingDirectory(dir)
        launch_info.SetLaunchFlags(eLaunchFlagNone)
        error = SBError()
        self.process = SBProcess(self.target.Launch(launch_info, error))
        if not error.Success() or not self.process.IsValid():
            raise ValueError
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

    @property
    def currentThread(self):
        return self.process.GetSelectedThread()

    @property
    def currentFrame(self):
        return self.currentThread.GetSelectedFrame()

    @property
    def currentFrameFile(self):
        file_spec = SBFileSpec(self.currentFrame.GetLineEntry().GetFileSpec())
        if file_spec.GetDirectory() is None or file_spec.GetFilename() is None:
            return None
        return str(file_spec.GetDirectory()) + '/' + str(file_spec.GetFilename())

    def addBreakpoint(self, file, line):
        self.target.BreakpointCreateByLocation(file, line)

    def removeBreakpoint(self, bp):
        self.target.BreakpointDelete(bp.GetID())

    def breakpoints(self, file=None, line=None):
        if file is None:
            if self.target is None:
                return []
            bps = []
            for i in range(self.target.GetNumBreakpoints()):
                bps.append(self.target.GetBreakpointAtIndex(i))
            return bps
        else:
            bps = self.breakpoints()
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

    @observable
    def pause(self):
        pass

    def debugLoop(self):
        event = SBEvent()
        while 1:
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

                        thread = SBThread(self.process.GetSelectedThread())
                        stream = SBStream()

                        thread.GetStatus(stream)
                        event.GetDescription(stream)

                        print stream.GetData()

                        stop_reason = thread.GetStopReason()
                        if stop_reason != eStopReasonInvalid:
                            frame = SBFrame(thread.GetSelectedFrame())

                            valueList = SBValueList(frame.GetVariables(True, True, False, True))

                            for i in range(valueList.GetSize()):
                                value = SBValue(valueList.GetValueAtIndex(i))
                                print value.GetName()

                        if stop_reason == eStopReasonBreakpoint:
                            for i in range(thread.GetStopReasonDataCount()):
                                print thread.GetStopReasonDataAtIndex(i)
                            thread.StepOver()

                        elif stop_reason == eStopReasonPlanComplete:
                            self.process.Continue()

                    else:
                        continue

                elif event_type == SBProcess.eBroadcastBitSTDOUT:
                    while True:
                        bytes = self.process.GetSTDOUT(1024)
                        if bytes:
                            print bytes
                        else:
                            break

                elif event_type == SBProcess.eBroadcastBitSTDERR:
                    while True:
                        bytes = self.process.GetSTDERR(1024)
                        if bytes:
                            print bytes
                        else:
                            break

                elif event_type == SBProcess.eBroadcastBitInterrupt:
                    print 'Interrupted'

            else:
                break

        print 'end'

