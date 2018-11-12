#! /usr/bin/python2.7
import lldb
import os
import sys


DIR = '/home/arman/dev/'
SOURCE = 'test.cpp'
TARGET = 'test'


if __name__ == '__main__':
    debugger = lldb.SBDebugger.Create()

    if debugger:
        print 'Debugger initialized'

        target = lldb.SBTarget(debugger.CreateTarget(DIR + TARGET))
        if target:
            print 'Target created'

            file_name = str(DIR + SOURCE)
            target.BreakpointCreateByLocation(file_name, 13)
            target.BreakpointCreateByLocation(file_name, 29)
            target.BreakpointCreateByLocation(file_name, 35)
            target.BreakpointCreateByLocation(file_name, 41)
            target.BreakpointCreateByLocation(file_name, 43)
            target.BreakpointCreateByLocation(file_name, 45)

            args = [DIR + TARGET]
            launch_info = lldb.SBLaunchInfo(args)
            launch_info.SetWorkingDirectory(DIR)
            launch_info.SetLaunchFlags(lldb.eLaunchFlagNone)
            error = lldb.SBError()
            process = target.Launch(launch_info, error)

            if not error.Success():
                print 'Error when trying to launch process'

            if process:
                print 'Process launched'
                print process

                event = lldb.SBEvent()

                listener = debugger.GetListener()

                while True:

                    if process.GetState() == lldb.eStateExited:
                        print 'Process finished'
                        break

                    if listener.WaitForEvent(5, event):
                        if not event.IsValid():
                            break

                        if not lldb.SBProcess.EventIsProcessEvent(event):
                            continue

                        event_type = event.GetType()
                        if event_type == lldb.SBProcess.eBroadcastBitStateChanged:
                            state = lldb.SBProcess.GetStateFromEvent(event)

                            if state == lldb.eStateStopped:
                                thread = process.GetSelectedThread()
                                stream = lldb.SBStream()

                                thread.GetStatus(stream)
                                event.GetDescription(stream)

                                stop_reason = thread.GetStopReason()
                                if stop_reason != lldb.eStopReasonInvalid:
                                    print '--- Stopped ---'
                                    frame = thread.GetSelectedFrame()
                                    frame.GetDescription(stream)

                                    valueList = frame.GetVariables(True, True, False, True)

                                    # print stream.GetData()

                                    for i in range(valueList.GetSize()):
                                        value = valueList.GetValueAtIndex(i)
                                        if str(value.GetType()).find('A *') > 0:
                                            child_vs = lldb.SBValue(value).GetChildMemberWithName('name')
                                            print(child_vs.GetSummary())

                                if stop_reason == lldb.eStopReasonBreakpoint:
                                    print '--- Stopped At Breakpoint ---'

                                    process.Continue()

                            else:
                                continue

                        elif event_type == lldb.SBProcess.eBroadcastBitSTDOUT:
                            print '------------'
                            while True:
                                bytes = process.GetSTDOUT(1024)
                                if bytes:
                                    print bytes
                                else:
                                    break

                        elif event_type == lldb.SBProcess.eBroadcastBitSTDERR:
                            print '============'
                            while True:
                                bytes = process.GetSTDERR(1024)
                                if bytes:
                                    print bytes
                                else:
                                    break

                    else:
                        print 'No event happened for 5 seconds'
                        break
