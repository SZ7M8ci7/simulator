var modalId;
var data;
var growATKDict = {
  SSRATK: 5.195,
  SSRBAL寄りATK: 4.865,
  SSRBAL: 4.7,
  SSRBAL寄りDEF: 4.535,
  SSRDEF: 4.205,
  SRATK: 4.735,
  SRBAL寄りATK: 4.445,
  SRBAL: 4.3,
  SRBAL寄りDEF: 4.155,
  SRDEF: 3.865,
  RATK: 4.62,
  RBAL寄りATK: 4.34,
  RBAL: 4.2,
  RBAL寄りDEF: 4.06,
  RDEF: 3.78,
};
var growHPDict = {
  SSRATK: 4.205,
  SSRBAL寄りATK: 4.535,
  SSRBAL: 4.7,
  SSRBAL寄りDEF: 4.865,
  SSRDEF: 5.195,
  SRATK: 3.865,
  SRBAL寄りATK: 4.155,
  SRBAL: 4.3,
  SRBAL寄りDEF: 4.445,
  SRDEF: 4.735,
  RATK: 3.78,
  RBAL寄りATK: 4.06,
  RBAL: 4.2,
  RBAL寄りDEF: 4.34,
  RDEF: 4.62,
};

var magicDict = {
  デュオ魔法5: "0.625",
  デュオ魔法6: "0.65",
  デュオ魔法7: "0.675",
  デュオ魔法8: "0.70",
  デュオ魔法9: "0.725",
  デュオ魔法10: "1.0",
  "連撃(弱)1": "0.525",
  "連撃(弱)2": "0.55",
  "連撃(弱)3": "0.575",
  "連撃(弱)4": "0.60",
  "連撃(弱)5": "0.625",
  "連撃(弱)6": "0.65",
  "連撃(弱)7": "0.675",
  "連撃(弱)8": "0.70",
  "連撃(弱)9": "0.725",
  "連撃(弱)10": "0.75",
  "連撃(強)1": "0.6625",
  "連撃(強)2": "0.70",
  "連撃(強)3": "0.7375",
  "連撃(強)4": "0.775",
  "連撃(強)5": "0.8125",
  "連撃(強)6": "0.85",
  "連撃(強)7": "0.8875",
  "連撃(強)8": "0.925",
  "連撃(強)9": "0.9625",
  "連撃(強)10": "1.0",
  "単発(弱)1": "0.525",
  "単発(弱)2": "0.55",
  "単発(弱)3": "0.575",
  "単発(弱)4": "0.60",
  "単発(弱)5": "0.625",
  "単発(弱)6": "0.65",
  "単発(弱)7": "0.675",
  "単発(弱)8": "0.70",
  "単発(弱)9": "0.725",
  "単発(弱)10": "0.75",
  "単発(強)1": "0.6625",
  "単発(強)2": "0.70",
  "単発(強)3": "0.7375",
  "単発(強)4": "0.775",
  "単発(強)5": "0.8125",
  "単発(強)6": "0.85",
  "単発(強)7": "0.8875",
  "単発(強)8": "0.925",
  "単発(強)9": "0.9625",
  "単発(強)10": "1.0",
};
var criticallDict = {
  "クリティカル(1/1)": 1.25,
  "クリティカル(1/2)": 1.125,
  "クリティカル(1/3)": 1.0833,
  "クリティカル(2/3)": 1.1666,
};
var atkbuffDict = {};
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKUP(極小)" + i] = ((5 + 0.5 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKUP(小)" + i] = ((10 + 1 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKUP(中)" + i] = ((20 + 1.5 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKUP(大)" + i] = ((30 + 2 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKUP(極大)" + i] = ((50 + 4 * i) / 100).toString();
}

for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKDOWN(極小)" + i] = (-1*(5 + 0.5 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKDOWN(小)" + i] = (-1*(10 + 1 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKDOWN(中)" + i] = (-1*(20 + 1.5 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKDOWN(大)" + i] = (-1*(30 + 2 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  atkbuffDict["ATKDOWN(極大)" + i] = (-1*(50 + 4 * i) / 100).toString();
}

var dmgbuffDict = {};
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメUP(極小)" + i] = ((1.25 + 0.125 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメUP(小)" + i] = ((2.5 + 0.25 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメUP(中)" + i] = ((5 + 0.375 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメUP(大)" + i] = ((7.5 + 0.5 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメUP(極大)" + i] = ((12.5 + 1 * i) / 100).toString();
}

for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメDOWN(極小)" + i] = (-1*(1.25 + 0.125 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメDOWN(小)" + i] = (-1*(2.5 + 0.25 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメDOWN(中)" + i] = (-1*(5 + 0.375 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメDOWN(大)" + i] = (-1*(7.5 + 0.5 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["ダメDOWN(極大)" + i] = (-1*(12.5 + 1 * i) / 100).toString();
}

for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメUP(極小)" + i] = ((1.5 + 0.15 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメUP(小)" + i] = ((3 + 0.3 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメUP(中)" + i] = ((6 + 0.45 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメUP(大)" + i] = ((9 + 0.6 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメUP(極大)" + i] = ((15 + 1.2 * i) / 100).toString();
}

for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメDOWN(極小)" + i] = (-1*(1.5 + 0.15 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメDOWN(小)" + i] = (-1*(3 + 0.3 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメDOWN(中)" + i] = (-1*(6 + 0.45 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメDOWN(大)" + i] = (-1*(9 + 0.6 * i) / 100).toString();
}
for (let i = 1; i <= 10; i++) {
  dmgbuffDict["属性ダメDOWN(極大)" + i] = (-1*(15 + 1.2 * i) / 100).toString();
}
var buddyHPDict = {
  "HPUP(小)1": "0.11",
  "HPUP(小)2": "0.12",
  "HPUP(小)3": "0.13",
  "HPUP(小)4": "0.14",
  "HPUP(小)5": "0.15",
  "HPUP(小)6": "0.16",
  "HPUP(小)7": "0.17",
  "HPUP(小)8": "0.18",
  "HPUP(小)9": "0.19",
  "HPUP(小)10": "0.20",
  "HPUP(中)1": "0.21",
  "HPUP(中)2": "0.22",
  "HPUP(中)3": "0.23",
  "HPUP(中)4": "0.24",
  "HPUP(中)5": "0.25",
  "HPUP(中)6": "0.26",
  "HPUP(中)7": "0.27",
  "HPUP(中)8": "0.28",
  "HPUP(中)9": "0.29",
  "HPUP(中)10": "0.30",
  "HP&ATKUP(小)1": "0.11",
  "HP&ATKUP(小)2": "0.12",
  "HP&ATKUP(小)3": "0.13",
  "HP&ATKUP(小)4": "0.14",
  "HP&ATKUP(小)5": "0.15",
  "HP&ATKUP(小)6": "0.16",
  "HP&ATKUP(小)7": "0.17",
  "HP&ATKUP(小)8": "0.18",
  "HP&ATKUP(小)9": "0.19",
  "HP&ATKUP(小)10": "0.20",
  "HP&ATKUP(中)1": "0.21",
  "HP&ATKUP(中)2": "0.22",
  "HP&ATKUP(中)3": "0.23",
  "HP&ATKUP(中)4": "0.24",
  "HP&ATKUP(中)5": "0.25",
  "HP&ATKUP(中)6": "0.26",
  "HP&ATKUP(中)7": "0.27",
  "HP&ATKUP(中)8": "0.28",
  "HP&ATKUP(中)9": "0.29",
  "HP&ATKUP(中)10": "0.30",
};
var buddyATKDict = {
  "ATKUP(小)1": "0.11",
  "ATKUP(小)2": "0.12",
  "ATKUP(小)3": "0.13",
  "ATKUP(小)4": "0.14",
  "ATKUP(小)5": "0.15",
  "ATKUP(小)6": "0.16",
  "ATKUP(小)7": "0.17",
  "ATKUP(小)8": "0.18",
  "ATKUP(小)9": "0.19",
  "ATKUP(小)10": "0.20",
  "ATKUP(中)1": "0.215",
  "ATKUP(中)2": "0.23",
  "ATKUP(中)3": "0.245",
  "ATKUP(中)4": "0.26",
  "ATKUP(中)5": "0.275",
  "ATKUP(中)6": "0.29",
  "ATKUP(中)7": "0.305",
  "ATKUP(中)8": "0.32",
  "ATKUP(中)9": "0.335",
  "ATKUP(中)10": "0.35",
  "HP&ATKUP(小)1": "0.11",
  "HP&ATKUP(小)2": "0.12",
  "HP&ATKUP(小)3": "0.13",
  "HP&ATKUP(小)4": "0.14",
  "HP&ATKUP(小)5": "0.15",
  "HP&ATKUP(小)6": "0.16",
  "HP&ATKUP(小)7": "0.17",
  "HP&ATKUP(小)8": "0.18",
  "HP&ATKUP(小)9": "0.19",
  "HP&ATKUP(小)10": "0.20",
  "HP&ATKUP(中)1": "0.215",
  "HP&ATKUP(中)2": "0.23",
  "HP&ATKUP(中)3": "0.245",
  "HP&ATKUP(中)4": "0.26",
  "HP&ATKUP(中)5": "0.275",
  "HP&ATKUP(中)6": "0.29",
  "HP&ATKUP(中)7": "0.305",
  "HP&ATKUP(中)8": "0.32",
  "HP&ATKUP(中)9": "0.335",
  "HP&ATKUP(中)10": "0.35",
};
var healDict = {
  "回復(極小)1": "0.51",
  "回復(極小)2": "0.52",
  "回復(極小)3": "0.53",
  "回復(極小)4": "0.54",
  "回復(極小)5": "0.55",
  "回復(極小)6": "0.56",
  "回復(極小)7": "0.57",
  "回復(極小)8": "0.58",
  "回復(極小)9": "0.59",
  "回復(極小)10": "0.60",
  "回復(小)1": "0.92",
  "回復(小)2": "0.94",
  "回復(小)3": "0.96",
  "回復(小)4": "0.98",
  "回復(小)5": "1.00",
  "回復(小)6": "1.02",
  "回復(小)7": "1.04",
  "回復(小)8": "1.06",
  "回復(小)9": "1.08",
  "回復(小)10": "1.10",
  "回復(中)1": "1.34",
  "回復(中)2": "1.38",
  "回復(中)3": "1.42",
  "回復(中)4": "1.46",
  "回復(中)5": "1.50",
  "回復(中)6": "1.54",
  "回復(中)7": "1.58",
  "回復(中)8": "1.62",
  "回復(中)9": "1.66",
  "回復(中)10": "1.70",
  "継続回復(小)1": "0",
  "継続回復(小)2": "0",
  "継続回復(小)3": "0",
  "継続回復(小)4": "0",
  "継続回復(小)5": "0",
  "継続回復(小)6": "0",
  "継続回復(小)7": "0",
  "継続回復(小)8": "0",
  "継続回復(小)9": "0",
  "継続回復(小)10": "0",
  "継続回復(中)1": "0",
  "継続回復(中)2": "0",
  "継続回復(中)3": "0",
  "継続回復(中)4": "0",
  "継続回復(中)5": "0",
  "継続回復(中)6": "0",
  "継続回復(中)7": "0",
  "継続回復(中)8": "0",
  "継続回復(中)9": "0",
  "継続回復(中)10": "0",
  "回復&継続回復(小)1": "0.92",
  "回復&継続回復(小)2": "0.94",
  "回復&継続回復(小)3": "0.96",
  "回復&継続回復(小)4": "0.98",
  "回復&継続回復(小)5": "1.00",
  "回復&継続回復(小)6": "1.02",
  "回復&継続回復(小)7": "1.04",
  "回復&継続回復(小)8": "1.06",
  "回復&継続回復(小)9": "1.08",
  "回復&継続回復(小)10": "1.10",
};
var healContinueDict = {
  "回復(極小)1": "0",
  "回復(極小)2": "0",
  "回復(極小)3": "0",
  "回復(極小)4": "0",
  "回復(極小)5": "0",
  "回復(極小)6": "0",
  "回復(極小)7": "0",
  "回復(極小)8": "0",
  "回復(極小)9": "0",
  "回復(極小)10": "0",
  "回復(小)1": "0",
  "回復(小)2": "0",
  "回復(小)3": "0",
  "回復(小)4": "0",
  "回復(小)5": "0",
  "回復(小)6": "0",
  "回復(小)7": "0",
  "回復(小)8": "0",
  "回復(小)9": "0",
  "回復(小)10": "0",
  "回復(中)1": "0",
  "回復(中)2": "0",
  "回復(中)3": "0",
  "回復(中)4": "0",
  "回復(中)5": "0",
  "回復(中)6": "0",
  "回復(中)7": "0",
  "回復(中)8": "0",
  "回復(中)9": "0",
  "回復(中)10": "0",
  "継続回復(小)1": "0.105",
  "継続回復(小)2": "0.11",
  "継続回復(小)3": "0.115",
  "継続回復(小)4": "0.12",
  "継続回復(小)5": "0.125",
  "継続回復(小)6": "0.13",
  "継続回復(小)7": "0.135",
  "継続回復(小)8": "0.14",
  "継続回復(小)9": "0.145",
  "継続回復(小)10": "0.15",
  "継続回復(中)1": "0.205",
  "継続回復(中)2": "0.21",
  "継続回復(中)3": "0.215",
  "継続回復(中)4": "0.22",
  "継続回復(中)5": "0.225",
  "継続回復(中)6": "0.23",
  "継続回復(中)7": "0.235",
  "継続回復(中)8": "0.24",
  "継続回復(中)9": "0.245",
  "継続回復(中)10": "0.25",
  "回復&継続回復(小)1": "0.105",
  "回復&継続回復(小)2": "0.11",
  "回復&継続回復(小)3": "0.115",
  "回復&継続回復(小)4": "0.12",
  "回復&継続回復(小)5": "0.125",
  "回復&継続回復(小)6": "0.13",
  "回復&継続回復(小)7": "0.135",
  "回復&継続回復(小)8": "0.14",
  "回復&継続回復(小)9": "0.145",
  "回復&継続回復(小)10": "0.15",
};
function setModal(id) {
  modalId = id;
}
function checkLimit(cb, no) {
  var checkboxes = document.getElementsByName("checkboxc" + no);
  var checkedCount = 0;
  for (var i = 0; i < checkboxes.length; i++) {
    if (checkboxes[i].checked) {
      checkedCount++;
    }
  }
  if (checkedCount > 2) {
    cb.checked = false;
  }
}
function changeImg(imgsrc) {
  var imgId = "img" + modalId;
  document.getElementById(imgId).src = "img/" + imgsrc + ".png";
  document.getElementById(imgId).value = "img/" + imgsrc + ".png";
  var totuRadioId = "ctotu" + modalId;
  document.getElementById(totuRadioId).checked = true;

  var atk = 0;
  for (let i = 0; i < data.length; i++) {
    if (data[i].name == imgsrc) {
      var level = 0;
      if (data[i].rare == "R") {
        level = 70;
      }
      if (data[i].rare == "SR") {
        level = 90;
      }
      if (data[i].rare == "SSR") {
        level = 110;
      }
      document.getElementById("cLv" + modalId).value = Number(level);
      document.getElementById("cLvhidden" + modalId).value = Number(level);
      document.getElementById("cGrowType" + modalId).value =
        data[i].rare + data[i].growtype;
      document.getElementById("cATK" + modalId).value = Number(data[i].atk);
      document.getElementById("cHP" + modalId).value = Number(data[i].hp);
      document.getElementById("cATKhidden" + modalId).value = Number(
        data[i].atk
      );
      document.getElementById("cHPhidden" + modalId).value = Number(data[i].hp);
      document.getElementById("cBaseATKhidden" + modalId).value = Number(
        data[i].base_atk
      );
      document.getElementById("cBaseHPhidden" + modalId).value = Number(
        data[i].base_hp
      );
      document.getElementById("cM1pow" + modalId).value = data[i].magic1pow;
      document.getElementById("cM1Atr" + modalId).value = data[i].magic1atr;
      document.getElementById("cM1buf1" + modalId).value = data[i].magic1buf;
      document.getElementById("cM1buf2" + modalId).value = "";
      document.getElementById("cM1heal" + modalId).value = data[i].magic1heal;
      document.getElementById("cM2pow" + modalId).value = data[i].magic2pow;
      document.getElementById("cM2Atr" + modalId).value = data[i].magic2atr;
      document.getElementById("cM2buf1" + modalId).value = data[i].magic2buf;
      document.getElementById("cM2buf2" + modalId).value = "";
      document.getElementById("cM2heal" + modalId).value = data[i].magic2heal;
      document.getElementById("cM3pow" + modalId).value = data[i].magic3pow;
      document.getElementById("cM3Atr" + modalId).value = data[i].magic3atr;
      document.getElementById("cM3buf1" + modalId).value = data[i].magic3buf;
      document.getElementById("cM3buf2" + modalId).value = "";
      document.getElementById("cM3heal" + modalId).value = data[i].magic3heal;
      document.getElementById("cbuddy1Name" + modalId).value = data[i].buddy1c;
      document.getElementById("cbuddy1St" + modalId).value = data[i].buddy1s;
      document.getElementById("cbuddy2Name" + modalId).value = data[i].buddy2c;
      document.getElementById("cbuddy2St" + modalId).value = data[i].buddy2s;
      document.getElementById("cbuddy3Name" + modalId).value = data[i].buddy3c;
      document.getElementById("cbuddy3St" + modalId).value = data[i].buddy3s;
      document.getElementById("cduo" + modalId).innerHTML = data[i].duo;
      document.getElementById("cname" + modalId).value = data[i].chara;
      document.getElementById("cetc" + modalId).innerHTML = data[i].etc;
      document.getElementById("cM1Lv" + modalId).value = "10";
      document.getElementById("cM1buf1Lv" + modalId).value = "10";
      document.getElementById("cM1buf2Lv" + modalId).value = "10";
      document.getElementById("cM2Lv" + modalId).value = "10";
      document.getElementById("cM2buf1Lv" + modalId).value = "10";
      document.getElementById("cM2buf2Lv" + modalId).value = "10";
      document.getElementById("cbuddy1Lv" + modalId).value = "10";
      document.getElementById("cbuddy2Lv" + modalId).value = "10";
      document.getElementById("cbuddy3Lv" + modalId).value = "10";
      var dDict = { dummy: "dummy" };
      // デュオチェック用辞書作成
      for (let d = 1; d <= 5; d++) {
        if (document.getElementById("cname" + d).value != "") {
          dDict[document.getElementById("cname" + d).value] =
            document.getElementById("cname" + d).value;
        }
      }
      for (let d = 1; d <= 5; d++) {
        if (document.getElementById("cduo" + d).innerHTML in dDict) {
          document.getElementById("cM2pow" + d).value = "デュオ魔法";
        } else if (
          document.getElementById("cM2pow" + d).value == "デュオ魔法"
        ) {
          document.getElementById("cM2pow" + d).value = "連撃(強)";
        }
      }
      calc();
      setChart();
    }
  }
}

function changeLevel(inid) {
  var inLv = Number(document.getElementById("cLv" + inid).value);
  var hiddenLv = Number(document.getElementById("cLvhidden" + inid).value);
  var maxHP = Number(document.getElementById("cHPhidden" + inid).value);
  var maxATK = Number(document.getElementById("cATKhidden" + inid).value);
  var baseHP = Number(document.getElementById("cBaseHPhidden" + inid).value);
  var baseATK = Number(document.getElementById("cBaseATKhidden" + inid).value);
  const options = document.getElementsByName("ctotu" + inid + "options");
  let selectedOption;

  for (let i = 0; i < options.length; i++) {
    if (options[i].checked) {
      selectedOption = options[i].value;
      break;
    }
  }
  let totsurate = 0;
  if (selectedOption == "未") {
    totsurate = 1;
  }
  var bonusHP = baseHP*0.2;
  var bonusATK = baseATK*0.2;
  var HPperLv = (maxHP - 2*bonusHP - baseHP) / (hiddenLv - 1);
  var ATKperLv = (maxATK - 2*bonusATK - baseATK) / (hiddenLv - 1);
  var leveldef = hiddenLv - inLv;
  document.getElementById("cHP" + inid).value = (
    (maxHP - HPperLv * leveldef) - bonusHP*totsurate).toFixed(1);
  document.getElementById("cATK" + inid).value = (
    (maxATK - ATKperLv * leveldef) - bonusATK*totsurate).toFixed(1);
}
function calc() {
  try {
    var charaDict = { "": "" };

    // バディチェック用辞書作成
    for (let i = 1; i <= 5; i++) {
      charaDict[document.getElementById("cname" + i).value] =
        document.getElementById("cname" + i).value;
    }
    for (let i = 1; i <= 5; i++) {
      var buddy1Value = document.getElementById("cbuddy1Name" + i).value;
      if (buddy1Value !== "" && buddy1Value in charaDict) {
        var buddy1Select = document.getElementById("cbuddy1Name" + i);
        buddy1Select.style.color = "#fa8072"; // Set background color when matching
      } else {
        var buddy1Select = document.getElementById("cbuddy1Name" + i);
        buddy1Select.style.color = ""; // Reset background color when not matching
      }
    
      var buddy2Value = document.getElementById("cbuddy2Name" + i).value;
      if (buddy2Value !== "" && buddy2Value in charaDict) {
        var buddy2Select = document.getElementById("cbuddy2Name" + i);
        buddy2Select.style.color = "#fa8072"; // Set background color when matching
      } else {
        var buddy2Select = document.getElementById("cbuddy2Name" + i);
        buddy2Select.style.color = ""; // Reset background color when not matching
      }
    
      var buddy3Value = document.getElementById("cbuddy3Name" + i).value;
      if (buddy3Value !== "" && buddy3Value in charaDict) {
        var buddy3Select = document.getElementById("cbuddy3Name" + i);
        buddy3Select.style.color = "#fa8072"; // Set background color when matching
      } else {
        var buddy3Select = document.getElementById("cbuddy3Name" + i);
        buddy3Select.style.color = ""; // Reset background color when not matching
      }
    }
    
    var totalHP = 0;
    var totalHealHP = 0;
    // データ系列フィルタ処理
    var elements = document.getElementsByName("display");
    let len = elements.length;
    for (let i = 0; i < len; i++) {
      if (elements.item(i).checked) {
        filterAttribute = elements.item(i).value;
      }
    }
    var damageList = [];
    var damageDataList = [];
    for (let i = 1; i <= 5; i++) {
      const damageM1Data = new Object();
      const damageM2Data = new Object();
      const damageM3Data = new Object();
      var selected_magic = [];
      var checkboxes = document.getElementsByName("checkboxc" + i);
      for (var n = 0; n < checkboxes.length; n++) {
        if (checkboxes[n].checked) {
          selected_magic.push(n + 1);
        }
      }

      // HP回復計算ロジック
      var heal = 0;
      var heal1key =
        document.getElementById("cM1heal" + i).value +
        document.getElementById("cM1Lv" + i).value;
      var heal2key =
        document.getElementById("cM2heal" + i).value +
        document.getElementById("cM2Lv" + i).value;
      var heal3key =
        document.getElementById("cM3heal" + i).value +
        document.getElementById("cM3Lv" + i).value;
      var heal1 = heal1key in healDict ? healDict[heal1key] : 0;
      var heal2 = heal2key in healDict ? healDict[heal2key] : 0;
      var heal3 = heal3key in healDict ? healDict[heal3key] : 0;
      if (selected_magic.includes(1)) {
        heal +=
          Number(heal1) * Number(document.getElementById("cATK" + i).value);
      }
      if (selected_magic.includes(2)) {
        heal +=
          Number(heal2) * Number(document.getElementById("cATK" + i).value);
      }
      if (selected_magic.includes(3)) {
        heal +=
          Number(heal3) * Number(document.getElementById("cATK" + i).value);
      }

      var healc1 =
        heal1key in healContinueDict ? healContinueDict[heal1key] : 0;
      var healc2 =
        heal2key in healContinueDict ? healContinueDict[heal2key] : 0;
      var healc3 =
        heal3key in healContinueDict ? healContinueDict[heal3key] : 0;
      if (selected_magic.includes(1)) {
        heal +=
          3 * Number(healc1) * Number(document.getElementById("cHP" + i).value);
      }
      if (selected_magic.includes(2)) {
        heal +=
          3 * Number(healc2) * Number(document.getElementById("cHP" + i).value);
      }
      if (selected_magic.includes(3)) {
        heal +=
          3 * Number(healc3) * Number(document.getElementById("cHP" + i).value);
      }
      document.getElementById("cHPheal" + i).value = heal.toFixed(1);

      // バディHP計算ロジック
      var buddy1hpRatio = 0;
      var buddy2hpRatio = 0;
      var buddy3hpRatio = 0;
      var buddy1key =
        document.getElementById("cbuddy1St" + i).value +
        document.getElementById("cbuddy1Lv" + i).value;
      if (document.getElementById("cbuddy1Name" + i).value in charaDict) {
        buddy1hpRatio = buddy1key in buddyHPDict ? buddyHPDict[buddy1key] : 0;
      }
      var buddy2key =
        document.getElementById("cbuddy2St" + i).value +
        document.getElementById("cbuddy2Lv" + i).value;
      if (document.getElementById("cbuddy2Name" + i).value in charaDict) {
        buddy2hpRatio = buddy2key in buddyHPDict ? buddyHPDict[buddy2key] : 0;
      }
      var buddy3key =
        document.getElementById("cbuddy3St" + i).value +
        document.getElementById("cbuddy3Lv" + i).value;
      if (document.getElementById("cbuddy3Name" + i).value in charaDict) {
        buddy3hpRatio = buddy3key in buddyHPDict ? buddyHPDict[buddy3key] : 0;
      }
      var tmpHP = Number(document.getElementById("cHP" + i).value);
      var buddyhp =
        buddy1hpRatio * tmpHP + buddy2hpRatio * tmpHP + buddy3hpRatio * tmpHP;
      document.getElementById("cHPbuddy" + i).value = buddyhp.toFixed(1);
      totalHP += buddyhp + tmpHP;
      totalHealHP += buddyhp + tmpHP + heal;

      // バディATK計算ロジック
      var buddy1atkRatio = 0;
      var buddy2atkRatio = 0;
      var buddy3atkRatio = 0;
      var buddy1key =
        document.getElementById("cbuddy1St" + i).value +
        document.getElementById("cbuddy1Lv" + i).value;
      if (document.getElementById("cbuddy1Name" + i).value in charaDict) {
        buddy1atkRatio =
          buddy1key in buddyATKDict ? buddyATKDict[buddy1key] : 0;
      }
      var buddy2key =
        document.getElementById("cbuddy2St" + i).value +
        document.getElementById("cbuddy2Lv" + i).value;
      if (document.getElementById("cbuddy2Name" + i).value in charaDict) {
        buddy2atkRatio =
          buddy2key in buddyATKDict ? buddyATKDict[buddy2key] : 0;
      }
      var buddy3key =
        document.getElementById("cbuddy3St" + i).value +
        document.getElementById("cbuddy3Lv" + i).value;
      if (document.getElementById("cbuddy3Name" + i).value in charaDict) {
        buddy3atkRatio =
          buddy3key in buddyATKDict ? buddyATKDict[buddy3key] : 0;
      }
      var tmpATK = document.getElementById("cATK" + i).value;
      var buddyatk =
        buddy1atkRatio * tmpATK +
        buddy2atkRatio * tmpATK +
        buddy3atkRatio * tmpATK;
      document.getElementById("cATKbuddy" + i).value = buddyatk.toFixed(1);
      var suATK = Number(document.getElementById("cATK" + i).value);
      // magick1計算ロジック

      var M1attribute = document.getElementById("cM1Atr" + i).value;
      var M1atkbuf1 =
        document.getElementById("cM1buf1" + i).value +
        document.getElementById("cM1buf1Lv" + i).value;
      var M1atkbuf2 =
        document.getElementById("cM1buf2" + i).value +
        document.getElementById("cM1buf2Lv" + i).value;
      var M1atkbuf3 =
        document.getElementById("cM1buf3" + i).value +
        document.getElementById("cM1buf3Lv" + i).value;
      var M1atkbuf4 =
        document.getElementById("cM1buf4" + i).value +
        document.getElementById("cM1buf4Lv" + i).value;
      var M1atkbuf5 =
        document.getElementById("cM1buf5" + i).value +
        document.getElementById("cM1buf5Lv" + i).value;
      var M1atkbuf1add =
        (M1atkbuf1 in atkbuffDict ? atkbuffDict[M1atkbuf1] : 0) * suATK;
      var M1atkbuf2add =
        (M1atkbuf2 in atkbuffDict ? atkbuffDict[M1atkbuf2] : 0) * suATK;
      var M1atkbuf3add =
        (M1atkbuf3 in atkbuffDict ? atkbuffDict[M1atkbuf3] : 0) * suATK;
      var M1atkbuf4add =
        (M1atkbuf4 in atkbuffDict ? atkbuffDict[M1atkbuf4] : 0) * suATK;
      var M1atkbuf5add =
        (M1atkbuf5 in atkbuffDict ? atkbuffDict[M1atkbuf5] : 0) * suATK;

      var M1kou1 = suATK + M1atkbuf1add + M1atkbuf2add + M1atkbuf3add + M1atkbuf4add + M1atkbuf5add + buddyatk;

      // 攻撃倍率
      var M1magicRatioKey =
        document.getElementById("cM1pow" + i).value +
        document.getElementById("cM1Lv" + i).value;
      var M1magicRatio =
        M1magicRatioKey in magicDict ? magicDict[M1magicRatioKey] : 0;
      // 無属性補正
      var M1muAdjust = M1attribute == "無" ? 1.1 : 1;
      // ダメージバフ
      var M1dmgbuf1 =
        document.getElementById("cM1buf1" + i).value +
        document.getElementById("cM1buf1Lv" + i).value;
      var M1dmgbuf2 =
        document.getElementById("cM1buf2" + i).value +
        document.getElementById("cM1buf2Lv" + i).value;
      var M1dmgbuf3 =
        document.getElementById("cM1buf3" + i).value +
        document.getElementById("cM1buf3Lv" + i).value;
      var M1dmgbuf4 =
        document.getElementById("cM1buf4" + i).value +
        document.getElementById("cM1buf4Lv" + i).value;
      var M1dmgbuf5 =
        document.getElementById("cM1buf5" + i).value +
        document.getElementById("cM1buf5Lv" + i).value;
      var M1dmgbuf1add = M1dmgbuf1 in dmgbuffDict ? dmgbuffDict[M1dmgbuf1] : 0;
      var M1dmgbuf2add = M1dmgbuf2 in dmgbuffDict ? dmgbuffDict[M1dmgbuf2] : 0;
      var M1dmgbuf3add = M1dmgbuf3 in dmgbuffDict ? dmgbuffDict[M1dmgbuf3] : 0;
      var M1dmgbuf4add = M1dmgbuf4 in dmgbuffDict ? dmgbuffDict[M1dmgbuf4] : 0;
      var M1dmgbuf5add = M1dmgbuf5 in dmgbuffDict ? dmgbuffDict[M1dmgbuf5] : 0;

      var M1kou2 =
        Number(M1magicRatio) * Number(M1muAdjust) +
        Number(M1dmgbuf1add) +
        Number(M1dmgbuf2add) +
        Number(M1dmgbuf3add) +
        Number(M1dmgbuf4add) +
        Number(M1dmgbuf5add);

      var M1rengeki = 1;
      var M1magicpow = document.getElementById("cM1pow" + i).value;
      if (M1magicpow == "連撃(弱)" || M1magicpow == "連撃(強)") {
        M1rengeki = 1.8;
      }
      if (M1magicpow == "デュオ魔法") {
        M1rengeki = 2.4;
      }
      var M1criticalbuf1 = document.getElementById("cM1buf1" + i).value;
      var M1criticalbuf2 = document.getElementById("cM1buf2" + i).value;
      var M1criticalbuf3 = document.getElementById("cM1buf3" + i).value;
      var M1criticalbuf4 = document.getElementById("cM1buf4" + i).value;
      var M1criticalbuf5 = document.getElementById("cM1buf5" + i).value;
      var M1criticalbuf1add = M1criticalbuf1 in criticallDict ? criticallDict[M1criticalbuf1] : 0;
      var M1criticalbuf2add = M1criticalbuf2 in criticallDict ? criticallDict[M1criticalbuf2] : 0;
      var M1criticalbuf3add = M1criticalbuf3 in criticallDict ? criticallDict[M1criticalbuf3] : 0;
      var M1criticalbuf4add = M1criticalbuf4 in criticallDict ? criticallDict[M1criticalbuf4] : 0;
      var M1criticalbuf5add = M1criticalbuf5 in criticallDict ? criticallDict[M1criticalbuf5] : 0;
      var M1damage = M1kou1 * M1kou2 * M1rengeki * Math.max(M1criticalbuf1add,M1criticalbuf2add,M1criticalbuf3add,M1criticalbuf4add,M1criticalbuf5add,1);
      var vsM1hidamage = (M1damage * 1).toFixed(1);
      var vsM1kidamage = (M1damage * 1).toFixed(1);
      var vsM1mizudamage = (M1damage * 1).toFixed(1);
      var vsM1mudamage = (M1damage * 1).toFixed(1);
      if (M1attribute == "火") {
        vsM1hidamage = (M1damage * 1).toFixed(1);
        vsM1kidamage = (M1damage * 1.5).toFixed(1);
        vsM1mizudamage = (M1damage * 0.5).toFixed(1);
      }
      if (M1attribute == "水") {
        vsM1hidamage = (M1damage * 1.5).toFixed(1);
        vsM1kidamage = (M1damage * 0.5).toFixed(1);
        vsM1mizudamage = (M1damage * 1).toFixed(1);
      }
      if (M1attribute == "木") {
        vsM1hidamage = (M1damage * 0.5).toFixed(1);
        vsM1kidamage = (M1damage * 1).toFixed(1);
        vsM1mizudamage = (M1damage * 1.5).toFixed(1);
      }
      document.getElementById("cM1HiDamage" + i).value = vsM1hidamage;
      document.getElementById("cM1KiDamage" + i).value = vsM1kidamage;
      document.getElementById("cM1MizuDamage" + i).value = vsM1mizudamage;
      document.getElementById("cM1MuDamage" + i).value = vsM1mudamage;
      damageM1Data.vszendamage = Math.max(
        Number(vsM1hidamage),
        Number(vsM1kidamage),
        Number(vsM1mizudamage)
      );
      damageM1Data.vshidamage = Number(vsM1hidamage);
      damageM1Data.vskidamage = Number(vsM1kidamage);
      damageM1Data.vsmizudamage = Number(vsM1mizudamage);
      damageM1Data.vsmudamage = Number(vsM1mudamage);
      damageM1Data.attribute = M1attribute;
      damageM1Data.duoMagic = M1magicpow;

      // magick2計算ロジック
      var M2attribute = document.getElementById("cM2Atr" + i).value;
      var M2atkbuf1 =
        document.getElementById("cM2buf1" + i).value +
        document.getElementById("cM2buf1Lv" + i).value;
      var M2atkbuf2 =
        document.getElementById("cM2buf2" + i).value +
        document.getElementById("cM2buf2Lv" + i).value;
      var M2atkbuf3 =
        document.getElementById("cM2buf3" + i).value +
        document.getElementById("cM2buf3Lv" + i).value;
      var M2atkbuf4 =
        document.getElementById("cM2buf4" + i).value +
        document.getElementById("cM2buf4Lv" + i).value;
      var M2atkbuf5 =
        document.getElementById("cM2buf5" + i).value +
        document.getElementById("cM2buf5Lv" + i).value;
      var M2atkbuf1add =
        (M2atkbuf1 in atkbuffDict ? atkbuffDict[M2atkbuf1] : 0) * suATK;
      var M2atkbuf2add =
        (M2atkbuf2 in atkbuffDict ? atkbuffDict[M2atkbuf2] : 0) * suATK;
      var M2atkbuf3add =
        (M2atkbuf3 in atkbuffDict ? atkbuffDict[M2atkbuf3] : 0) * suATK;
      var M2atkbuf4add =
        (M2atkbuf4 in atkbuffDict ? atkbuffDict[M2atkbuf4] : 0) * suATK;
      var M2atkbuf5add =
        (M2atkbuf5 in atkbuffDict ? atkbuffDict[M2atkbuf5] : 0) * suATK;

      var M2kou1 = suATK + M2atkbuf1add + M2atkbuf2add + M2atkbuf3add + M2atkbuf4add + M2atkbuf5add + buddyatk;

      // 攻撃倍率
      var M2magicRatioKey =
        document.getElementById("cM2pow" + i).value +
        document.getElementById("cM2Lv" + i).value;
      var M2magicRatio =
        M2magicRatioKey in magicDict ? magicDict[M2magicRatioKey] : 0;
      // 無属性補正
      var M2muAdjust = M2attribute == "無" ? 1.1 : 1;
      // ダメージバフ
      var M2dmgbuf1 =
        document.getElementById("cM2buf1" + i).value +
        document.getElementById("cM2buf1Lv" + i).value;
      var M2dmgbuf2 =
        document.getElementById("cM2buf2" + i).value +
        document.getElementById("cM2buf2Lv" + i).value;
      var M2dmgbuf3 =
        document.getElementById("cM2buf3" + i).value +
        document.getElementById("cM2buf3Lv" + i).value;
      var M2dmgbuf4 =
        document.getElementById("cM2buf4" + i).value +
        document.getElementById("cM2buf4Lv" + i).value;
      var M2dmgbuf5 =
        document.getElementById("cM2buf5" + i).value +
        document.getElementById("cM2buf5Lv" + i).value;
      var M2dmgbuf1add = M2dmgbuf1 in dmgbuffDict ? dmgbuffDict[M2dmgbuf1] : 0;
      var M2dmgbuf2add = M2dmgbuf2 in dmgbuffDict ? dmgbuffDict[M2dmgbuf2] : 0;
      var M2dmgbuf3add = M2dmgbuf3 in dmgbuffDict ? dmgbuffDict[M2dmgbuf3] : 0;
      var M2dmgbuf4add = M2dmgbuf4 in dmgbuffDict ? dmgbuffDict[M2dmgbuf4] : 0;
      var M2dmgbuf5add = M2dmgbuf5 in dmgbuffDict ? dmgbuffDict[M2dmgbuf5] : 0;

      var M2kou2 =
        Number(M2magicRatio) * Number(M2muAdjust) +
        Number(M2dmgbuf1add) +
        Number(M2dmgbuf2add) +
        Number(M2dmgbuf3add) +
        Number(M2dmgbuf4add) +
        Number(M2dmgbuf5add);

      var M2rengeki = 1;
      var M2magicpow = document.getElementById("cM2pow" + i).value;
      if (M2magicpow == "連撃(弱)" || M2magicpow == "連撃(強)") {
        M2rengeki = 1.8;
      }
      if (M2magicpow == "デュオ魔法") {
        M2rengeki = 2.4;
      }
      var M2criticalbuf1 = document.getElementById("cM2buf1" + i).value;
      var M2criticalbuf2 = document.getElementById("cM2buf2" + i).value;
      var M2criticalbuf3 = document.getElementById("cM2buf3" + i).value;
      var M2criticalbuf4 = document.getElementById("cM2buf4" + i).value;
      var M2criticalbuf5 = document.getElementById("cM2buf5" + i).value;
      var M2criticalbuf1add = M2criticalbuf1 in criticallDict ? criticallDict[M2criticalbuf1] : 0;
      var M2criticalbuf2add = M2criticalbuf2 in criticallDict ? criticallDict[M2criticalbuf2] : 0;
      var M2criticalbuf3add = M2criticalbuf3 in criticallDict ? criticallDict[M2criticalbuf3] : 0;
      var M2criticalbuf4add = M2criticalbuf4 in criticallDict ? criticallDict[M2criticalbuf4] : 0;
      var M2criticalbuf5add = M2criticalbuf5 in criticallDict ? criticallDict[M2criticalbuf5] : 0;
      var M2damage = M2kou1 * M2kou2 * M2rengeki * Math.max(M2criticalbuf1add,M2criticalbuf2add,M2criticalbuf3add,M2criticalbuf4add,M2criticalbuf5add,1);
      var vsM2hidamage = (M2damage * 1).toFixed(1);
      var vsM2kidamage = (M2damage * 1).toFixed(1);
      var vsM2mizudamage = (M2damage * 1).toFixed(1);
      var vsM2mudamage = (M2damage * 1).toFixed(1);
      if (M2attribute == "火") {
        vsM2hidamage = (M2damage * 1).toFixed(1);
        vsM2kidamage = (M2damage * 1.5).toFixed(1);
        vsM2mizudamage = (M2damage * 0.5).toFixed(1);
      }
      if (M2attribute == "水") {
        vsM2hidamage = (M2damage * 1.5).toFixed(1);
        vsM2kidamage = (M2damage * 0.5).toFixed(1);
        vsM2mizudamage = (M2damage * 1).toFixed(1);
      }
      if (M2attribute == "木") {
        vsM2hidamage = (M2damage * 0.5).toFixed(1);
        vsM2kidamage = (M2damage * 1).toFixed(1);
        vsM2mizudamage = (M2damage * 1.5).toFixed(1);
      }
      document.getElementById("cM2HiDamage" + i).value = vsM2hidamage;
      document.getElementById("cM2KiDamage" + i).value = vsM2kidamage;
      document.getElementById("cM2MizuDamage" + i).value = vsM2mizudamage;
      document.getElementById("cM2MuDamage" + i).value = vsM2mudamage;
      damageM2Data.vszendamage = Math.max(
        Number(vsM2hidamage),
        Number(vsM2kidamage),
        Number(vsM2mizudamage)
      );
      damageM2Data.vshidamage = Number(vsM2hidamage);
      damageM2Data.vskidamage = Number(vsM2kidamage);
      damageM2Data.vsmizudamage = Number(vsM2mizudamage);
      damageM2Data.vsmudamage = Number(vsM2mudamage);
      damageM2Data.attribute = M2attribute;
      damageM2Data.duoMagic = M2magicpow;

      // magick3計算ロジック
      var M3attribute = document.getElementById("cM3Atr" + i).value;
      var M3atkbuf1 =
        document.getElementById("cM3buf1" + i).value +
        document.getElementById("cM3buf1Lv" + i).value;
      var M3atkbuf2 =
        document.getElementById("cM3buf2" + i).value +
        document.getElementById("cM3buf2Lv" + i).value;
      var M3atkbuf3 =
        document.getElementById("cM3buf3" + i).value +
        document.getElementById("cM3buf3Lv" + i).value;
      var M3atkbuf4 =
        document.getElementById("cM3buf4" + i).value +
        document.getElementById("cM3buf4Lv" + i).value;
      var M3atkbuf5 =
        document.getElementById("cM3buf5" + i).value +
        document.getElementById("cM3buf5Lv" + i).value;
      var M3atkbuf1add =
        (M3atkbuf1 in atkbuffDict ? atkbuffDict[M3atkbuf1] : 0) * suATK;
      var M3atkbuf2add =
        (M3atkbuf2 in atkbuffDict ? atkbuffDict[M3atkbuf2] : 0) * suATK;
      var M3atkbuf3add =
        (M3atkbuf3 in atkbuffDict ? atkbuffDict[M3atkbuf3] : 0) * suATK;
      var M3atkbuf4add =
        (M3atkbuf4 in atkbuffDict ? atkbuffDict[M3atkbuf4] : 0) * suATK;
      var M3atkbuf5add =
        (M3atkbuf5 in atkbuffDict ? atkbuffDict[M3atkbuf5] : 0) * suATK;

      var M3kou1 = suATK + M3atkbuf1add + M3atkbuf2add + M3atkbuf3add + M3atkbuf4add + M3atkbuf5add + buddyatk;

      // 攻撃倍率
      var M3magicRatioKey =
        document.getElementById("cM3pow" + i).value +
        document.getElementById("cM3Lv" + i).value;
      var M3magicRatio =
        M3magicRatioKey in magicDict ? magicDict[M3magicRatioKey] : 0;
      // 無属性補正
      var M3muAdjust = M3attribute == "無" ? 1.1 : 1;
      // ダメージバフ
      var M3dmgbuf1 =
        document.getElementById("cM3buf1" + i).value +
        document.getElementById("cM3buf1Lv" + i).value;
      var M3dmgbuf2 =
        document.getElementById("cM3buf2" + i).value +
        document.getElementById("cM3buf2Lv" + i).value;
      var M3dmgbuf3 =
        document.getElementById("cM3buf3" + i).value +
        document.getElementById("cM3buf3Lv" + i).value;
      var M3dmgbuf4 =
        document.getElementById("cM3buf4" + i).value +
        document.getElementById("cM3buf4Lv" + i).value;
      var M3dmgbuf5 =
        document.getElementById("cM3buf5" + i).value +
        document.getElementById("cM3buf5Lv" + i).value;
      var M3dmgbuf1add = M3dmgbuf1 in dmgbuffDict ? dmgbuffDict[M3dmgbuf1] : 0;
      var M3dmgbuf2add = M3dmgbuf2 in dmgbuffDict ? dmgbuffDict[M3dmgbuf2] : 0;
      var M3dmgbuf3add = M3dmgbuf3 in dmgbuffDict ? dmgbuffDict[M3dmgbuf3] : 0;
      var M3dmgbuf4add = M3dmgbuf4 in dmgbuffDict ? dmgbuffDict[M3dmgbuf4] : 0;
      var M3dmgbuf5add = M3dmgbuf5 in dmgbuffDict ? dmgbuffDict[M3dmgbuf5] : 0;

      var M3kou2 =
        Number(M3magicRatio) * Number(M3muAdjust) +
        Number(M3dmgbuf1add) +
        Number(M3dmgbuf2add) +
        Number(M3dmgbuf3add) +
        Number(M3dmgbuf4add) +
        Number(M3dmgbuf5add);

      var M3rengeki = 0;
      var M3magicpow = document.getElementById("cM3pow" + i).value;
      if (M3magicpow == "連撃(弱)" || M3magicpow == "連撃(強)") {
        M3rengeki = 1.8;
      }
      if (M3magicpow == "デュオ魔法") {
        M3rengeki = 2.4;
      }

      var M3criticalbuf1 = document.getElementById("cM3buf1" + i).value;
      var M3criticalbuf2 = document.getElementById("cM3buf2" + i).value;
      var M3criticalbuf3 = document.getElementById("cM3buf3" + i).value;
      var M3criticalbuf4 = document.getElementById("cM3buf4" + i).value;
      var M3criticalbuf5 = document.getElementById("cM3buf5" + i).value;
      var M3criticalbuf1add = M3criticalbuf1 in criticallDict ? criticallDict[M3criticalbuf1] : 0;
      var M3criticalbuf2add = M3criticalbuf2 in criticallDict ? criticallDict[M3criticalbuf2] : 0;
      var M3criticalbuf3add = M3criticalbuf3 in criticallDict ? criticallDict[M3criticalbuf3] : 0;
      var M3criticalbuf4add = M3criticalbuf4 in criticallDict ? criticallDict[M3criticalbuf4] : 0;
      var M3criticalbuf5add = M3criticalbuf5 in criticallDict ? criticallDict[M3criticalbuf5] : 0;
      var M3damage = M3kou1 * M3kou2 * M3rengeki * Math.max(M3criticalbuf1add,M3criticalbuf2add,M3criticalbuf3add,M3criticalbuf4add,M3criticalbuf5add,1);
      var vsM3hidamage = (M3damage * 1).toFixed(1);
      var vsM3kidamage = (M3damage * 1).toFixed(1);
      var vsM3mizudamage = (M3damage * 1).toFixed(1);
      var vsM3mudamage = (M3damage * 1).toFixed(1);
      if (M3attribute == "火") {
        vsM3hidamage = (M3damage * 1).toFixed(1);
        vsM3kidamage = (M3damage * 1.5).toFixed(1);
        vsM3mizudamage = (M3damage * 0.5).toFixed(1);
      }
      if (M3attribute == "水") {
        vsM3hidamage = (M3damage * 1.5).toFixed(1);
        vsM3kidamage = (M3damage * 0.5).toFixed(1);
        vsM3mizudamage = (M3damage * 1).toFixed(1);
      }
      if (M3attribute == "木") {
        vsM3hidamage = (M3damage * 0.5).toFixed(1);
        vsM3kidamage = (M3damage * 1).toFixed(1);
        vsM3mizudamage = (M3damage * 1.5).toFixed(1);
      }
      document.getElementById("cM3HiDamage" + i).value = vsM3hidamage;
      document.getElementById("cM3KiDamage" + i).value = vsM3kidamage;
      document.getElementById("cM3MizuDamage" + i).value = vsM3mizudamage;
      document.getElementById("cM3MuDamage" + i).value = vsM3mudamage;
      damageM3Data.vszendamage = Math.max(
        Number(vsM3hidamage),
        Number(vsM3kidamage),
        Number(vsM3mizudamage)
      );
      damageM3Data.vshidamage = Number(vsM3hidamage);
      damageM3Data.vskidamage = Number(vsM3kidamage);
      damageM3Data.vsmizudamage = Number(vsM3mizudamage);
      damageM3Data.vsmudamage = Number(vsM3mudamage);
      damageM3Data.attribute = M3attribute;
      damageM3Data.duoMagic = M3magicpow;
      if (selected_magic.includes(1)) {
        damageDataList.push(damageM1Data);
      }
      if (selected_magic.includes(2)) {
        damageDataList.push(damageM2Data);
      }
      if (selected_magic.includes(3)) {
        damageDataList.push(damageM3Data);
      }
      if (filterAttribute == "全属性") {
        if (selected_magic.includes(1)) {
          damageList.push(
            Math.max(vsM1hidamage, vsM1kidamage, vsM1mizudamage, vsM1mudamage)
          );
        }
        if (selected_magic.includes(2)) {
          damageList.push(
            Math.max(vsM2hidamage, vsM2kidamage, vsM2mizudamage, vsM2mudamage)
          );
        }
        if (selected_magic.includes(3)) {
          damageList.push(
            Math.max(vsM3hidamage, vsM3kidamage, vsM3mizudamage, vsM3mudamage)
          );
        }
      }
      if (filterAttribute == "対火属性") {
        if (selected_magic.includes(1)) {
          damageList.push(Number(vsM1hidamage));
        }
        if (selected_magic.includes(2)) {
          damageList.push(Number(vsM2hidamage));
        }
        if (selected_magic.includes(3)) {
          damageList.push(Number(vsM3hidamage));
        }
      }
      if (filterAttribute == "対木属性") {
        if (selected_magic.includes(1)) {
          damageList.push(Number(vsM1kidamage));
        }
        if (selected_magic.includes(2)) {
          damageList.push(Number(vsM2kidamage));
        }
        if (selected_magic.includes(3)) {
          damageList.push(Number(vsM3kidamage));
        }
      }
      if (filterAttribute == "対水属性") {
        if (selected_magic.includes(1)) {
          damageList.push(Number(vsM1mizudamage));
        }
        if (selected_magic.includes(2)) {
          damageList.push(Number(vsM2mizudamage));
        }
        if (selected_magic.includes(3)) {
          damageList.push(Number(vsM3mizudamage));
        }
      }
      if (filterAttribute == "対無属性") {
        if (selected_magic.includes(1)) {
          damageList.push(Number(vsM1mudamage));
        }
        if (selected_magic.includes(2)) {
          damageList.push(Number(vsM2mudamage));
        }
        if (selected_magic.includes(3)) {
          damageList.push(Number(vsM3mudamage));
        }
      }
    }
    let score = [0, 0, 0, 0, 0];
    if (filterAttribute == "全属性") {
      let result = damageDataList.sort(function (a, b) {
        return a.vszendamage > b.vszendamage ? -1 : 1; //オブジェクトの降順ソート
      });
      for (j = 0; j < 5; j++) {
        for (k = 2 * j; k < 2 * j + 2; k++) {
          for (l = j; l < 5; l++) {
            if (!result[k]) {
              continue;
            }
            if (result[k].duoMagic == "デュオ魔法") {
              score[l] += 3000;
            }
            score[l] += 1500;
            score[l] += result[k].vszendamage;
            score[l] += 500;
          }
        }
      }
    }
    if (filterAttribute == "対火属性") {
      let result = damageDataList.sort(function (a, b) {
        return a.vshidamage > b.vshidamage ? -1 : 1; //オブジェクトの降順ソート
      });
      for (j = 0; j < 5; j++) {
        for (k = 2 * j; k < 2 * j + 2; k++) {
          for (l = j; l < 5; l++) {
            if (!result[k]) {
              continue;
            }

            if (result[k].duoMagic == "デュオ魔法") {
              score[l] += 3000;
            }
            if (result[k].attribute == "水") {
              score[l] += 1500;
            }
            if (result[k].attribute == "木") {
              score[l] -= 1500;
            }
            score[l] += result[k].vshidamage;
            score[l] += 500;
          }
        }
      }
    }
    if (filterAttribute == "対木属性") {
      let result = damageDataList.sort(function (a, b) {
        return a.vskidamage > b.vskidamage ? -1 : 1; //オブジェクトの降順ソート
      });
      for (j = 0; j < 5; j++) {
        for (k = 2 * j; k < 2 * j + 2; k++) {
          for (l = j; l < 5; l++) {
            if (!result[k]) {
              continue;
            }

            if (result[k].duoMagic == "デュオ魔法") {
              score[l] += 3000;
            }
            if (result[k].attribute == "火") {
              score[l] += 1500;
            }
            if (result[k].attribute == "水") {
              score[l] -= 1500;
            }
            score[l] += result[k].vskidamage;
            score[l] += 500;
          }
        }
      }
    }
    if (filterAttribute == "対水属性") {
      let result = damageDataList.sort(function (a, b) {
        return a.vsmizudamage > b.vsmizudamage ? -1 : 1; //オブジェクトの降順ソート
      });
      for (j = 0; j < 5; j++) {
        for (k = 2 * j; k < 2 * j + 2; k++) {
          for (l = j; l < 5; l++) {
            if (!result[k]) {
              continue;
            }
            if (result[k].duoMagic == "デュオ魔法") {
              score[l] += 3000;
            }
            if (result[k].attribute == "木") {
              score[l] += 1500;
            }
            if (result[k].attribute == "火") {
              score[l] -= 1500;
            }
            score[l] += result[k].vsmizudamage;
            score[l] += 500;
          }
        }
      }
    }
    if (filterAttribute == "対無属性") {
      let result = damageDataList.sort(function (a, b) {
        return a.vsmudamage > b.vsmudamage ? -1 : 1; //オブジェクトの降順ソート
      });
      for (j = 0; j < 5; j++) {
        for (k = 2 * j; k < 2 * j + 2; k++) {
          for (l = j; l < 5; l++) {
            if (!result[k]) {
              continue;
            }
            if (result[k].duoMagic == "デュオ魔法") {
              score[l] += 3000;
            }
            score[l] += result[k].vsmudamage;
            score[l] += 500;
          }
        }
      }
    }
    damageList.sort(function (a, b) {
      return b - a;
    });
    damage3 =
      (damageList[0] || 0) +
      (damageList[1] || 0) +
      (damageList[2] || 0) +
      (damageList[3] || 0) +
      (damageList[4] || 0) +
      (damageList[5] || 0);
    damage4 = damage3 + (damageList[6] || 0) + (damageList[7] || 0);
    damage5 = damage4 + (damageList[8] || 0) + (damageList[9] || 0);

    document.getElementById("totalHP").innerHTML = totalHP.toFixed();
    document.getElementById("totalHealHP").innerHTML = totalHealHP.toFixed();
    document.getElementById("totalDamage5").innerHTML = damage5.toFixed();
    document.getElementById("totalDamage4").innerHTML = damage4.toFixed();
    document.getElementById("totalDamage3").innerHTML = damage3.toFixed();
    document.getElementById("midDamage5").innerHTML = (damage5 - (damageList[0]||0)).toFixed() + '+' + (damageList[0]||0).toFixed();
    document.getElementById("midDamage4").innerHTML = (damage4 - (damageList[0]||0)).toFixed() + '+' + (damageList[0]||0).toFixed();
    document.getElementById("midDamage3").innerHTML = (damage3 - (damageList[0]||0)).toFixed() + '+' + (damageList[0]||0).toFixed();

    document.getElementById("extrascore1T").innerHTML = (
      score[0] * 0.216
    ).toFixed();
    document.getElementById("extrascore2T").innerHTML = (
      score[1] * 0.207
    ).toFixed();
    document.getElementById("extrascore3T").innerHTML = (
      score[2] * 0.198
    ).toFixed();
    document.getElementById("extrascore4T").innerHTML = (
      score[3] * 0.189
    ).toFixed();
    document.getElementById("extrascore5T").innerHTML = (
      score[4] * 0.15
    ).toFixed();

    document.getElementById("hardscore1T").innerHTML = (
      score[0] * 0.1728
    ).toFixed();
    document.getElementById("hardscore2T").innerHTML = (
      score[1] * 0.1656
    ).toFixed();
    document.getElementById("hardscore3T").innerHTML = (
      score[2] * 0.1584
    ).toFixed();
    document.getElementById("hardscore4T").innerHTML = (
      score[3] * 0.1512
    ).toFixed();
    document.getElementById("hardscore5T").innerHTML = (
      score[4] * 0.12
    ).toFixed();

    document.getElementById("normalscore1T").innerHTML = (
      score[0] * 0.144
    ).toFixed();
    document.getElementById("normalscore2T").innerHTML = (
      score[1] * 0.138
    ).toFixed();
    document.getElementById("normalscore3T").innerHTML = (
      score[2] * 0.132
    ).toFixed();
    document.getElementById("normalscore4T").innerHTML = (
      score[3] * 0.126
    ).toFixed();
    document.getElementById("normalscore5T").innerHTML = (
      score[4] * 0.1
    ).toFixed();

    document.getElementById("easyscore1T").innerHTML = (
      score[0] * 0.1152
    ).toFixed();
    document.getElementById("easyscore2T").innerHTML = (
      score[1] * 0.1104
    ).toFixed();
    document.getElementById("easyscore3T").innerHTML = (
      score[2] * 0.1056
    ).toFixed();
    document.getElementById("easyscore4T").innerHTML = (
      score[3] * 0.1008
    ).toFixed();
    document.getElementById("easyscore5T").innerHTML = (
      score[4] * 0.08
    ).toFixed();
  } catch {}
}
$myChart = 0;
function setChart() {
  if ($myChart != 0) $myChart.destroy();
  var ctx = document.getElementById("chart01").getContext("2d");
  var w = $(".contents").width();
  var h = $(".contents").height();
  $("#chart01").attr("width", 900);
  $("#chart01").attr("height", 250);

  fulldata = [
    {
      label: "HP",
      stack: "Stack 0",
      backgroundColor: "rgba(100, 100, 100, 0.6)",
      data: [
        document.getElementById("cHP1").value,
        document.getElementById("cHP2").value,
        document.getElementById("cHP3").value,
        document.getElementById("cHP4").value,
        document.getElementById("cHP5").value,
      ],
    },
    {
      label: "バディ",
      stack: "Stack 0",
      backgroundColor: "rgba(100, 100, 100, 0.4)",
      data: [
        document.getElementById("cHPbuddy1").value,
        document.getElementById("cHPbuddy2").value,
        document.getElementById("cHPbuddy3").value,
        document.getElementById("cHPbuddy4").value,
        document.getElementById("cHPbuddy5").value,
      ],
    },
    {
      label: "回復",
      stack: "Stack 0",
      backgroundColor: "rgba(100, 100, 100, 0.2)",
      data: [
        document.getElementById("cHPheal1").value,
        document.getElementById("cHPheal2").value,
        document.getElementById("cHPheal3").value,
        document.getElementById("cHPheal4").value,
        document.getElementById("cHPheal5").value,
      ],
    },
    {
      label: "対火(M1)",
      stack: "Stack 1",
      backgroundColor: "rgba(255, 20, 20, 0.4)",
      data: [
        document.getElementById("cM1HiDamage1").value,
        document.getElementById("cM1HiDamage2").value,
        document.getElementById("cM1HiDamage3").value,
        document.getElementById("cM1HiDamage4").value,
        document.getElementById("cM1HiDamage5").value,
      ],
    },
    {
      label: "対木(M1)",
      stack: "Stack 2",
      backgroundColor: "rgba(20, 255, 20, 0.4)",
      data: [
        document.getElementById("cM1KiDamage1").value,
        document.getElementById("cM1KiDamage2").value,
        document.getElementById("cM1KiDamage3").value,
        document.getElementById("cM1KiDamage4").value,
        document.getElementById("cM1KiDamage5").value,
      ],
    },
    {
      label: "対水(M1)",
      stack: "Stack 3",
      backgroundColor: "rgba(20, 20, 255, 0.4)",
      data: [
        document.getElementById("cM1MizuDamage1").value,
        document.getElementById("cM1MizuDamage2").value,
        document.getElementById("cM1MizuDamage3").value,
        document.getElementById("cM1MizuDamage4").value,
        document.getElementById("cM1MizuDamage5").value,
      ],
    },
    {
      label: "対無(M1)",
      stack: "Stack 4",
      backgroundColor: "rgba(140, 140, 140, 0.4)",
      data: [
        document.getElementById("cM1MuDamage1").value,
        document.getElementById("cM1MuDamage2").value,
        document.getElementById("cM1MuDamage3").value,
        document.getElementById("cM1MuDamage4").value,
        document.getElementById("cM1MuDamage5").value,
      ],
    },
    {
      label: "対火(M2)",
      stack: "Stack 5",
      backgroundColor: "rgba(255, 20, 20, 0.4)",
      data: [
        document.getElementById("cM2HiDamage1").value,
        document.getElementById("cM2HiDamage2").value,
        document.getElementById("cM2HiDamage3").value,
        document.getElementById("cM2HiDamage4").value,
        document.getElementById("cM2HiDamage5").value,
      ],
    },
    {
      label: "対木(M2)",
      stack: "Stack 6",
      backgroundColor: "rgba(20, 255, 20, 0.4)",
      data: [
        document.getElementById("cM2KiDamage1").value,
        document.getElementById("cM2KiDamage2").value,
        document.getElementById("cM2KiDamage3").value,
        document.getElementById("cM2KiDamage4").value,
        document.getElementById("cM2KiDamage5").value,
      ],
    },
    {
      label: "対水(M2)",
      stack: "Stack 7",
      backgroundColor: "rgba(20, 20, 255, 0.4)",
      data: [
        document.getElementById("cM2MizuDamage1").value,
        document.getElementById("cM2MizuDamage2").value,
        document.getElementById("cM2MizuDamage3").value,
        document.getElementById("cM2MizuDamage4").value,
        document.getElementById("cM2MizuDamage5").value,
      ],
    },
    {
      label: "対無(M2)",
      stack: "Stack 8",
      backgroundColor: "rgba(140, 140, 140, 0.4)",
      data: [
        document.getElementById("cM2MuDamage1").value,
        document.getElementById("cM2MuDamage2").value,
        document.getElementById("cM2MuDamage3").value,
        document.getElementById("cM2MuDamage4").value,
        document.getElementById("cM2MuDamage5").value,
      ],
    },
    {
      label: "対火(M3)",
      stack: "Stack 9",
      backgroundColor: "rgba(255, 20, 20, 0.4)",
      data: [
        document.getElementById("cM3HiDamage1").value,
        document.getElementById("cM3HiDamage2").value,
        document.getElementById("cM3HiDamage3").value,
        document.getElementById("cM3HiDamage4").value,
        document.getElementById("cM3HiDamage5").value,
      ],
    },
    {
      label: "対木(M3)",
      stack: "Stack 10",
      backgroundColor: "rgba(20, 255, 20, 0.4)",
      data: [
        document.getElementById("cM3KiDamage1").value,
        document.getElementById("cM3KiDamage2").value,
        document.getElementById("cM3KiDamage3").value,
        document.getElementById("cM3KiDamage4").value,
        document.getElementById("cM3KiDamage5").value,
      ],
    },
    {
      label: "対水(M3)",
      stack: "Stack 11",
      backgroundColor: "rgba(20, 20, 255, 0.4)",
      data: [
        document.getElementById("cM3MizuDamage1").value,
        document.getElementById("cM3MizuDamage2").value,
        document.getElementById("cM3MizuDamage3").value,
        document.getElementById("cM3MizuDamage4").value,
        document.getElementById("cM3MizuDamage5").value,
      ],
    },
    {
      label: "対無(M3)",
      stack: "Stack 12",
      backgroundColor: "rgba(140, 140, 140, 0.4)",
      data: [
        document.getElementById("cM3MuDamage1").value,
        document.getElementById("cM3MuDamage2").value,
        document.getElementById("cM3MuDamage3").value,
        document.getElementById("cM3MuDamage4").value,
        document.getElementById("cM3MuDamage5").value,
      ],
    },
  ];
  // データ系列フィルタ処理
  var elements = document.getElementsByName("display");
  let len = elements.length;
  for (let i = 0; i < len; i++) {
    if (elements.item(i).checked) {
      filterAttribute = elements.item(i).value;
    }
  }
  if (filterAttribute == "対火属性") {
    fulldata.splice(4, 3);
    fulldata.splice(5, 3);
    fulldata.splice(6, 3);
  }
  if (filterAttribute == "対木属性") {
    fulldata.splice(3, 1);
    fulldata.splice(4, 3);
    fulldata.splice(5, 3);
    fulldata.splice(6, 2);
  }
  if (filterAttribute == "対水属性") {
    fulldata.splice(3, 2);
    fulldata.splice(4, 3);
    fulldata.splice(5, 3);
    fulldata.splice(6, 1);
  }
  if (filterAttribute == "対無属性") {
    fulldata.splice(3, 3);
    fulldata.splice(4, 3);
    fulldata.splice(5, 3);
  }

  Chart.Tooltip.positioners.custom = function (elements, position) {
    if (!elements.length) {
      return false;
    }
    const ps = elements[0].tooltipPosition();
    const area = elements[0]._chart.chartArea;
    return {
      x: ps.x,
      y: area.top,
    };
  };
  $myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [
        document.getElementById("cname1").value,
        document.getElementById("cname2").value,
        document.getElementById("cname3").value,
        document.getElementById("cname4").value,
        document.getElementById("cname5").value,
      ],
      datasets: fulldata,
    },
    options: {
      scales: {
        xAxes: [
          {
            id: "x-axis",
            stacked: true,
          },
        ],
        yAxes: [
          {
            id: "y-axis",
            stacked: true,
            display: true,
            position: "left",
            ticks: {
              beginAtZero: true,
              min: 0,
            },
          },
        ],
      },
      legend: {
        position: "right", // タイトルでの position と同じ
      },
      tooltips: {
        mode: "label",
        position: "custom",
        caretSize: 0,
      },
      responsive: false,
      maintainAspectRatio: false,
    },
  });
}

function into() {
  var query = decodeURI(window.location.search).substring(1);
  var parms = query.split("%26");
  for (var i = 0; i < parms.length; i++) {
    var pos = parms[i].indexOf("=");
    if (pos > 0) {
      var key = parms[i].substring(0, pos);
      var val = parms[i].substring(pos + 1);
      if (key.indexOf("img") != -1) {
        var ind = key.indexOf("img");
        var iid = key.slice(key.indexOf("img") + 3);
        setModal(iid);
        changeImg(val.replace("img/", "").replace(".png", ""));
      }
    }
  }
  for (var i = 0; i < parms.length; i++) {
    var pos = parms[i].indexOf("=");
    if (pos > 0) {
      var key = parms[i].substring(0, pos);
      var val = parms[i].substring(pos + 1);
      var element = document.getElementById(key);
      if (key == "display") {
        // データ系列フィルタ処理
        var elements = document.getElementsByName("display");
        let len = elements.length;
        for (let i = 0; i < len; i++) {
          if (elements.item(i).value == val) {
            elements.item(i).checked = true;
          }
        }
        continue;
      }
      element.value = val;
    }
  }
}
function saveState() {
  const inputs = document.querySelectorAll("input");
  const selects = document.querySelectorAll("select");

  let state = [];

  inputs.forEach((input) => {
    let inputState = {
      id: input.id,
      value: input.value,
      type: input.type,
      checked: input.checked, // チェックボックスとラジオボタンの状態
    };
    state.push(inputState);
  });

  selects.forEach((select) => {
    let selectState = {
      id: select.id,
      value: select.value,
    };
    state.push(selectState);
  });

  // 状態をシリアライズして保存
  localStorage.setItem("pageState", JSON.stringify(state)); // シリアライズ必須
}

function openInNewTab() {
  saveState(); // 状態を保存

  // URLに?restoreState=trueが既に含まれているかどうかをチェック
  const restoreStateParam = "restoreState=true";
  let newUrl = window.location.href;

  if (!newUrl.includes(restoreStateParam)) {
    // URLに?または&を適切に追加
    newUrl += newUrl.includes("?") ? "&" : "?";
    newUrl += restoreStateParam; // restoreState=trueパラメータを追加
  }

  window.open(newUrl, "_blank"); // 新しいタブで修正したURLを開く
}

function restoreState() {
  const savedState = localStorage.getItem("pageState");
  if (savedState) {
    const state = JSON.parse(savedState); // パース必須

    // imgに続く数字一桁のidを持つ要素の特別処理を最初に行う
    state.forEach((item) => {
      const match = item.id.match(/^img(\d)$/);
      if (match && item.type === "image") {
        // 画像のURLを扱うinput想定
        const element = document.getElementById(item.id);
        if (element) {
          modalId = match[1]; // 数字一桁をmodalIdにセット
          changeImg(item.value.replace("img/", "").replace(".png", "")); // changeImg関数を呼び出し
          item.processed = true; // このアイテムが処理されたことをマーク
        }
      }
    });

    // その他の要素を復元
    state.forEach((item) => {
      // すでに処理されたアイテムはスキップ
      if (item.processed) return;

      const element = document.getElementById(item.id);
      if (element) {
        if (
          element.tagName === "INPUT" &&
          (element.type === "checkbox" || element.type === "radio")
        ) {
          element.checked = item.checked;
        } else if (
          element.tagName === "INPUT" ||
          element.tagName === "SELECT"
        ) {
          element.value = item.value;
        }
      }
    });
  }
}

function restoreURL() {
  const urlParams = new URLSearchParams(window.location.search);
  let index = 1;
  // クエリパラメータの値を取得して処理
  urlParams.forEach((value, key) => {
    if (key.startsWith("name")) {
        setModal(index);
        changeImg(value);
        index++;
    }
  });
}

window.addEventListener("DOMContentLoaded", function () {
  var inform = document.getElementById("myForm");
  inform.addEventListener("change", function () {
    calc();
    setChart();
  });
  inform.addEventListener("input", function () {
    calc();
    setChart();
  });
});
window.addEventListener("load", function () {
  $.getJSON("chara.json") // json読み込み開始
    .done(function (json) {
      data = json;
      const queryParams = new URLSearchParams(window.location.search);
      if (queryParams.get("restoreState") === "true") {
        restoreState();
      } else if (queryParams.get("restoreURL") === "true") {
        restoreURL();
      }
      calc();
      setChart();
      document.getElementById("loading").style.display = "none";
    });
});
$(function () {
  //input属性のものを一括で取得する
  var inputItem = document.getElementsByTagName("input");
  //ループしながら全てに処理を行う
  for (var i = 0; i < inputItem.length; i++) {
    //項目がreadonlyの場合のみ処理
    if (inputItem[i].readOnly) {
      //背景色を設定する
      inputItem[i].style.border = "0px";
      //タブ遷移を不可にする
      inputItem[i].tabIndex = "-1";
    }
  }
});
