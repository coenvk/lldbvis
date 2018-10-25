#! /usr/bin/python2.7
import lldb
import os
import sys


DIR = '/home/arman/dev/'
SOURCE = 'test.cpp'
TARGET = 'test'


if __name__ == '__main__':
    debugger = lldb.SBDebugger(lldb.SBDebugger.Create())

    if debugger:
        print 'Debugger initialized'

        target = lldb.SBTarget(debugger.CreateTarget(DIR + TARGET))
        if target:
            print 'Target created'

            bp = target.BreakpointCreateByName('main', target.GetExecutable().GetFilename())

            if bp:
                print 'Breakpoint set'
                print bp

            args = [DIR + TARGET]
            launch_info = lldb.SBLaunchInfo(args)
            launch_info.SetWorkingDirectory(DIR)
            launch_info.SetLaunchFlags(lldb.eLaunchFlagNone)
            error = lldb.SBError()
            process = lldb.SBProcess(target.Launch(launch_info, error))

            if not error.Success():
                print 'Error when trying to launch process'

            if process:
                print 'Process launched'
                print process

                event = lldb.SBEvent()

                listener = lldb.SBListener(debugger.GetListener())

                while True:

                    if process.GetState() == lldb.eStateExited:
                        print 'Process finished'
                        break

                    if listener.WaitForEvent(5, event):
                        if not event:
                            break

                        if not lldb.SBProcess.EventIsProcessEvent(event):
                            continue

                        event_type = event.GetType()
                        if event_type == lldb.SBProcess.eBroadcastBitStateChanged:
                            state = lldb.SBProcess.GetStateFromEvent(event)

                            if state == lldb.eStateStopped:
                                thread = lldb.SBThread(process.GetSelectedThread())
                                stream = lldb.SBStream()

                                thread.GetStatus(stream)
                                event.GetDescription(stream)

                                stop_reason = thread.GetStopReason()
                                if stop_reason != lldb.eStopReasonInvalid:
                                    print '--- Begin Data ---'
                                    frame = lldb.SBFrame(thread.GetFrameAtIndex(0))
                                    frame.GetDescription(stream)

                                    valueList = lldb.SBValueList(frame.GetVariables(True, True, False, True))

                                    print stream.GetData()

                                    for i in range(valueList.GetSize()):
                                        value = lldb.SBValue(valueList.GetValueAtIndex(i))
                                        print 'Value type: ' + value.GetDisplayTypeName()
                                        print 'Value name: ' + value.GetName()

                                    print '--- End Data ---'

                                if stop_reason == lldb.eStopReasonBreakpoint:
                                    bpId = thread.GetStopReasonDataAtIndex(0)
                                    if bpId == bp.GetID():
                                        print 'Stopped at breakpoint: ' + str(bpId)

                                    thread.StepOver()
                                elif stop_reason == lldb.eStopReasonPlanComplete:
                                    print 'Stopped at step'
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
                            print '------------'

                    else:
                        print 'No event happened for 5 seconds'
                        break
