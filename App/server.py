import threading, json, time
from . import ControlTemplate
import flask as fl
import requests


class ServerControl(ControlTemplate):
    def __init__(self, host) -> None:
        super().__init__(host)
        self.WebServer = fl.Flask(__name__)
        self.ThreadServer = threading.Thread(target=self.threadServer, daemon=True)
        self.BufferOutput = list()
        return

    def init(self):
        @self.WebServer.route("/Control")
        def control():
            return self.respControl()

        @self.WebServer.route("/<path:p>", methods=["GET"])
        def file(p):
            return fl.send_file("../Web/" + p)

        @self.WebServer.route("/command", methods=["POST"])
        def command():
            return self.respCommand()

        @self.WebServer.route("/operate", methods=["POST"])
        def operate():
            return self.respOperate()

        @self.WebServer.route("/pullOutput", methods=["POST"])
        def pullOutput():
            return self.respPullOutput()

        @self.WebServer.route("/postVision", methods=["POST"])
        def postVision():
            return self.respPostVision()

        return

    def startThread(self):
        if not self.ThreadServer.is_alive():
            self.ThreadServer = threading.Thread(target=self.threadServer, daemon=True)
            self.ThreadServer.start()
        return

    def threadServer(self):
        GSC = self.Host
        self.WebServer.run(host=GSC.getOption("MainHost"))
        return

    # 响应方法。
    def respControl(self):
        return fl.send_file("../Web/Control.html")

    def respPullOutput(self):
        ret = fl.jsonify({"Log": self.BufferOutput})
        self.BufferOutput.clear()
        return ret

    def recordInfo(self, data):
        self.BufferOutput.append(data)
        if len(self.BufferOutput) > 50:
            self.BufferOutput = self.BufferOutput[1:]
        return

    def respCommand(self):
        try:
            recv_data = fl.request.data.decode("utf-8")
            j = json.loads(recv_data)
            if "Command" in j:
                self.Host.execCommand(j["Command"])
        except BaseException as e:
            self.Host.info(str(e))
        return self.respPullOutput()

    def respOperate(self):
        LSC = self.Host
        try:
            recv_data = fl.request.data.decode("utf-8")
            j = json.loads(recv_data)
            ret = dict()
            if "Operation" in j:
                if j["Operation"] == "lift":
                    LSC.switchMode("Lifting")
                if j["Operation"] == "terminate":
                    LSC.switchMode("Idle")
                elif j["Operation"] == "sync":
                    ret = {"Mode": LSC.Mode, "Stage": LSC.CtrlLift.Stage}
                elif j["Operation"] == "login":
                    if j["AdminPass"] == LSC.getOption("AdminPass"):
                        LSC.info("Admin logined.")

                    else:
                        ret = {"Msg": "Password incorrect."}
                        raise BaseException(ret["Msg"])
        except BaseException as e:
            LSC.info(str(e))
            return fl.jsonify({"Result": 500, "Return": ret})
        return fl.jsonify({"Result": 200, "Return": ret})

    def respPostVision(self):
        """供内置视觉访问。"""
        GSC = self.Host

        file = fl.request.files.get("Image")
        if file is not None:
            t = time.localtime()
            timestr = str(t.tm_hour) + "-" + str(t.tm_min) + "-" + str(t.tm_sec)
            fdict = fl.request.form
            boxes = eval(fdict["Boxes"])
            res = GSC.CtrlVideo.saveBoxes(boxes)
            if res:
                GSC.PathEvidence = "tmp/vision - " + timestr + ".png"
                file.save(GSC.PathEvidence)
        return fl.jsonify({"code": 200, "msg": ""})

    pass
