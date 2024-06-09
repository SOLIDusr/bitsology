class Version:
    def __init__(self, vString: str):
        self.vString = vString
        self.vMajor, self.vMinor, self.vPatch, self.vType, self.vBuild = self.parce(vString)
    

    def __eq__(self, __value: object) -> int:
        if not isinstance(__value, Version):
            raise ValueError("Can't compare Version to non-Version")

        if self.vMajor > __value.vMajor:
            return -1
        elif self.vMajor < __value.vMajor:
            return 5
        if self.vMinor > __value.vMinor:
            return -1
        elif self.vMinor < __value.vMinor:
            return 4
        if self.vPatch > __value.vPatch:
            return -1
        elif self.vPatch < __value.vPatch:
            return 3
        if self.vType in ["b", "a", 'rc']:
            return 2
        if self.vBuild > __value.vBuild:
            return -1
        elif self.vBuild < __value.vBuild:
            return 1
        return 0

    def __str__(self) -> str:
        return "v"+self.vMajor+"."+self.vMinor+"."+self.vPatch+"-"+self.vType+self.vBuild

    def parce(self, vString: str):
        vString = vString.replace("v.", "")
        vString = vString.replace("-", ".")
        vString = vString.split(".")
        vMajor = ""
        vMinor = ""
        vPatch = ""
        vType = ""
        vBuild = ""
        if len(vString) > 3:
            if len(vString[3]) > 1:
                vType = "".join([ch for ch in vString[3] if ch.isalpha()])
                vBuild = "".join([ch for ch in vString[3] if ch.isdigit()])
            else:
                vType = vString[3]
                vBuild = "0"
        return vString[0], vString[1], vString[2], vType, vBuild
