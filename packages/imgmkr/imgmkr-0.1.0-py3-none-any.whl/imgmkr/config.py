import json, copy,traceback


class Config:
    def __init__(self, config_file="imgmkr.cfg"):
        self.config_file = config_file
        self._cfg = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._cfg = json.load(f)
        except Exception as e:
            traceback.print_exc()
            self._cfg = {}

    def save_config(self):
        print("save", self._cfg)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._cfg, f, indent=4, ensure_ascii=False)

    def getLastWorkDir(self):
        return self._cfg.get("last_work_dir", "")

    def setLastWorkDir(self, work_dir):
        self._cfg["last_work_dir"] = work_dir

    def getLabelHistory(self):
        return self._cfg.get("label_history", {})

    def setLabelHistory(self, history):
        self._cfg["label_history"] = copy.deepcopy(history)

    def getKeypointHistory(self):
        return self._cfg.get("keypoint_history", {})

    def setKeypointHistory(self, history):
        self._cfg["keypoint_history"] = copy.deepcopy(history)

    def getDetectorScript(self):
        return self._cfg.get("detector_script", "")

    def setDetectorScript(self, model_path):
        self._cfg["detector_script"] = model_path

    def getScripts(self):
        return self._cfg.get("scripts", [])

    def setScripts(self, scripts):
        self._cfg["scripts"] = scripts

    def addScript(self, script):
        if self._cfg.get("scripts") is None:
            self._cfg["scripts"] = []
        self._cfg["scripts"].append(script)

    def removeScript(self, script):
        if self._cfg.get("scripts") is not None:
            if script in self._cfg["scripts"]:
                self._cfg["scripts"].remove(script)

cfg = Config()
