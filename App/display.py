import json, socket, math, time, threading


class DisplayControl:
    def __init__(self, host) -> None:
        from LSS import LiftSuperviseSystem

        self.Host: LiftSuperviseSystem = host
        self.PipeRecv = None
        self.PipeSend = None

        self.Command = ""
        self.CmdArgs = 0
        self.FlagThreadRun = True

        self.ThdDisp = threading.Thread(target=self.threadDisplay, daemon=True)

        return

    def init(self):
        GSC = self.Host

        try:
            self.PipeRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.PipeRecv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.PipeRecv.settimeout(3)
            self.PipeRecv.bind(
                (GSC.getOption("MainHost"), GSC.getOption("DisplaySendPort"))
            )

            self.PipeSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.PipeSend.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.PipeSend.settimeout(3)
            self.PipeSend.bind((GSC.getOption("MainHost"), 2303))
            self.FlagThreadRun = True
            return True
        except BaseException as e:
            if str(e) != "timed out":
                GSC.info("Display launch failed: " + str(e))
        return False

    def threadDisplay(self):
        from App import readBit

        GSC = self.Host
        while self.FlagThreadRun:
            try:
                data_screen, address = self.PipeRecv.recvfrom(1024)
                jdata = json.loads(data_screen.decode())
            except BaseException as e:
                if str(e) != "timed out":
                    GSC.info("Screen Radio: " + str(e))
                continue

            if jdata["Type"] == "SC":
                self.Command = jdata["Command"]
                self.CmdArgs = jdata["Args"]

                ret = {
                    "Type": "SCR",
                    "Count": jdata["Count"],
                    "DeviceID": jdata["DeviceID"],
                    "Time": str(time.time() * 1000 // 1),
                    "Result": 0,
                }
                self.sendDisplay(ret)
            if jdata["Type"] == "CCR":
                if jdata["Result"] != 0:
                    self.Command = "startScreenTimer"

            GSC.info(self.Command)
            if self.Command == "startTimer":
                GSC.startTimer(src="Display")
            elif self.Command == "stopTimer":
                GSC.stopTimer(src="Display")
            elif self.Command == "demarcate":
                GSC.switchMode("Demarcation")
                if self.CmdArgs == 0:
                    GSC.Area = {
                        "Objects": list(),
                        "StageConfigure": [[1, 0, 0, 0]],
                    }
                elif self.CmdArgs != 0:
                    if self.CmdArgs == 1:
                        GSC.Area["OffsetSlew"] = round(
                            GSC.getCondition("Slew") - 180, 4
                        )
                        GSC.Area["OffsetHeight"] = round(GSC.getCondition("Height"), 4)
                        r = 1.5
                        h = 0.0
                        z = 0
                        GSC.info(GSC.Area["OffsetSlew"])
                    elif self.CmdArgs == 2:
                        r = 1.15  # 1.0
                        h = 0.0
                        z = 0
                    elif self.CmdArgs == 3:
                        r = 0.03  # 0.0125
                        h = 2.0
                        z = 1.0
                    elif self.CmdArgs == 4:
                        r = 1
                        h = GSC.Area["OffsetHeight"] - GSC.getCondition("Height")
                        z = 0
                    elif self.CmdArgs == 5:
                        r = round(0.2 / 1.414, 3)
                        h = 0.3
                        z = GSC.Area["OffsetHeight"] - GSC.getCondition("Height") - 0.15
                    elif self.CmdArgs == 6:
                        r = 0.05
                        h = 0  # 1.1
                        z = 0  # 0.55
                    elif self.CmdArgs == 7:
                        r = 1.0 / 1.414
                        h = GSC.Area["OffsetHeight"] - GSC.getCondition("Height")
                        z = h / 2
                    elif self.CmdArgs == 8:
                        r = 1
                        h = GSC.Area["OffsetHeight"] - GSC.getCondition("Height")
                        z = 0
                    theta = math.radians(
                        GSC.getCondition("Slew") - GSC.Area["OffsetSlew"]
                    )
                    x = GSC.getCondition("Radius") * math.cos(theta)
                    y = GSC.getCondition("Radius") * math.sin(theta)
                    obj = {
                        "ID": len(GSC.Area["Objects"]) + 1,
                        "Type": self.CmdArgs,
                        "X": round(x, 4),
                        "Y": round(y, 4),
                        "Z": round(z, 4),
                        "R": r,
                        "H": h,
                        "Floor": 0,
                        "Stage": GSC.Stage,
                    }
                    GSC.Area["Objects"].append(obj)
                    GSC.info(obj)
            elif self.Command == "exitDemarcation":
                from App import prettyFloats

                GSC.switchMode("Normal")
                if self.CmdArgs == 1:
                    path = "Conf/MatchArea_New.json"
                else:
                    path = "Conf/FinalArea_New.json"
                with open(path, "w+") as fd:
                    fd.truncate(0)
                    json.dump(prettyFloats(GSC.Area), fd, indent=4)
                area = {
                    "Type": "Demarcation",
                    "Slew": GSC.Area["OffsetSlew"],
                    "Height": GSC.Area["OffsetHeight"],
                    "Objects": list(),
                    "StageConfigure": GSC.Area["StageConfigure"],
                }
                for obj in GSC.Area["Objects"]:
                    area["Objects"].append(
                        [
                            obj["ID"],
                            obj["Type"],
                            obj["X"],
                            obj["Y"],
                            obj["Z"],
                            obj["R"],
                            obj["H"],
                            obj["Floor"],
                            obj["Stage"],
                        ]
                    )
                GSC.sendMqtt(area)
                GSC.CtrlVideo.sendArea(area)
            elif self.Command == "undoDemarcation":
                GSC.Area["Objects"].pop()
            elif self.Command == "exitExam":
                GSC.exitExam()
            elif self.Command == "switchStage":
                d = self.CmdArgs - len(GSC.Area["StageConfigure"])
                if d > 0:
                    for i in range(d):
                        GSC.Area["StageConfigure"].append([1, 0, 0, 0])
                GSC.Stage = self.CmdArgs
            elif self.Command == "confStage":
                tmp = list()
                for i in range(4):
                    tmp.append(int(readBit(self.CmdArgs, i)))
                GSC.Area["StageConfigure"][GSC.Stage - 1] = tmp
            elif self.Command == "enterExam":
                GSC.enterExam()

            self.Command = ""

        return

    def startThread(self):
        if not self.ThdDisp.is_alive():
            self.ThdDisp = threading.Thread(target=self.threadDisplay, daemon=True)
            self.ThdDisp.start()
        return

    def sendDisplay(self, dat):
        """dat为str时，作为命令发送。"""
        GSC = self.Host
        if isinstance(dat, str):
            data = {
                "Type": "CC",
                "Count": 0,
                "Command": "",
                "Args": 0,
            }
            if dat == "startTimer":
                data["Command"] = dat
                GSC.info("Display Command: start timer.")
            elif dat == "exitExam":
                data["Command"] = dat
                GSC.info("Display Command: exit exam.")
            elif dat == "stopTimer":
                data["Command"] = dat
                GSC.info("Display Command: stop timer.")
            # elif dat == "terminateComm":
            #     data["Command"] = dat
            #     GSC.info("Display Command: terminate communication.")
        else:
            data = dat

        addr = (
            self.Host.getOption("DisplayHost"),
            self.Host.getOption("DisplayRecvPort"),
        )
        self.PipeSend.sendto(json.dumps(data).encode(), addr)

        # self.PipeSend.sendto(json.dumps(data).encode(), ("192.168.102.102", 1303))
        # self.PipeSend.sendto(json.dumps(data).encode(), ("192.168.103.102", 1303))
        # self.PipeSend.sendto(json.dumps(data).encode(), ("192.168.104.102", 1303))
        return

    pass
