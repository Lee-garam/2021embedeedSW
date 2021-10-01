

const api = require("./tools/apitools"); // API class 분리.
const TTS = require("./tools/assistant.js");
const express = require("express");
const app = express();

const path = require("path");
const request = require("request");

const $KEY =
  "LzzZSX1HVpuOt6ll+18VXaapRGdF+uZmlytO16XLqD3r3vboeWmT1zElxNflUzm7xtfYUXZrL80JfNaDP0zYWg==";
const $arsid = "06175";
const stn_support_list = { "06175": "http://localhost:5000" }; //P1-P2 계산 지원하는 정류장 목록

// for test purpose
const $tmX = 127.0347743864;
const $tmY = 37.5881473927;
console.log("Start");

app.get("/", (main_req, main_res) => {
  main_res.sendFile(path.join(__dirname, "./html/main.html"));
});
app.get("/css/style.css", (main_req, main_res) => {
  main_res.sendFile(path.join(__dirname, "./html/main.css"));
});

app.get("/data/pos", async (main_req, main_res) => {
  let busapi = new api.getStationByPos($KEY);
  let tmX = main_req.query.tmX;
  let tmY = main_req.query.tmY;

  let radius = 100; //500m
  let accuracy = main_req.query.acc;
  if (typeof tmX == undefined || typeof tmY == undefined) {
    main_res.send();
    return;
  }

  // radius 반경 내 버스정류장 목록 불러오기
  // 5번 시도하며 점점 범위 넓힘
  let data;
  for (i = radius; i < radius * 4; i += radius) {
    let stnlist = await busapi.get($tmX, $tmY, i);
    data = JSON.stringify(stnlist);
    console.log(`${i}m 내 가까운 정류장(정확도 ${accuracy}): ${data}`);
    console.log(data);
    if (data != "[]") break;
  }
  main_res.send(data);
});

app.get("/data/buslist", async (main_req, main_res) => {
  let busapi = new api.getStationByUid($KEY);

  // arsid 받아오기
  let arsid = main_req.query.arsid;
  if (typeof arsid == undefined) {
    main_res.send();
    return;
  }

  // 버스정류장에서 P1, P2 리스트 받아오기
  let buslist = await busapi.get(arsid);
  let data = JSON.stringify(buslist);
  console.log(`정류장 버스 list: ${data}`);
  main_res.send(data);
});

// P1, P2 정보 가져오기
app.get("/data/station", (main_req, main_res) => {
  /*
  let arsid = main_req.query.arsid;
  if (typeof(arsid) == undefined){
        main_res.send();
        return;
    }
    */
  let options = {
    uri: stn_support_list[$arsid] + "/busdata/parking",
    headers: "Bypass-Tunnel-Reminder",
    timeout: 3000,
  };
  console.log(options.uri);
  request.get(options, (err, res, body) => {
    if (err) {
      console.warn(`station에서 P1, P2 정보를 가져올 수 없습니다. err: ${err}`);
      return;
    }
    console.log(body);
    main_res.send(body);
  }); // 디버깅용
});

// 승차벨 구현
app.get("/data/call", (main_req, main_res) => {
  rtnm = main_req.query.rtNm;
  //arsid = main_req.query.arsId;
  console.log(rtnm);
  if ((typeof $arsid == undefined) || (typeof rtnm == undefined)) {
    console.error("받은 승차벨 없음");
    main_res.send();
    return;
  }
  let options = {
    uri: stn_support_list[$arsid] + "/busdata/call",
    qs: {rtNm: rtnm},
    headers: "Bypass-Tunnel-Reminder",
    timeout: 3000,
  };
  request.get(options, (err, res, body) => {
    if (err) {
      console.warn(
        `station에 ${vehid} 승차벨 신호를 보낼 수 없습니다. err: ${err}`
      );
      main_res.send();
      return;
    }
    console.log("승차벨 신호: " + body);
    main_res.send(body);
  });
});

// TTS mp3 전송
app.get("/util/tts", async (main_req, main_res) => {
  text = main_req.query.text;
  main_res.setHeader("Content-Type", "audio/mpeg");
  main_res.send(await TTS.TTS(text));
});

app.listen(8080);
