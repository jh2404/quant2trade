from PyQt5.QtCore import *           # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from kiwoom import Kiwoom            # 로그인을 위한 클래스
from PyQt5.QtWidgets import *        # PyQt import
from PyQt5.QtTest import *           # 시간관련 함수
from datetime import datetime, timedelta    # 특정 일자를 조회

class Thread2(QThread):
    def __init__(self, parent):   # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)  # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent      # 부모의 윈도우를 사용하기 위한 조건


        ################## 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.k = Kiwoom()
        ##################

        ################## 사용되는 변수
        self.Find_down_Screen = "1200"         # 계좌평가잔고내역을 받기위한 스크린
        self.code_in_all = None

        ###### 슬롯
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다.
        ###### EventLoop
        self.detail_account_info_event_loop = QEventLoop()  # 계좌 이벤트루프
        
        self.C_K_F_class()
        

        ###### 결과 붙이기(gui)
        column_head = ["종목코드", "종목명", "위험도"]
        colCount = len(column_head)
        rowCount = len(self.k.acc_portfolio)
        self.parent.Danger_wd.setColumnCount(colCount)  # 행 갯수
        self.parent.Danger_wd.setRowCount(rowCount)  # 열 갯수 (종목 수)
        self.parent.Danger_wd.setHorizontalHeaderLabels(column_head)  # 행의 이름 삽입
        index2 = 0
        for k in self.k.acc_portfolio.keys():
            self.parent.Danger_wd.setItem(index2, 0, QTableWidgetItem(str(k))) # 종목코드
            self.parent.Danger_wd.setItem(index2, 1, QTableWidgetItem(self.k.acc_portfolio[k]["종목명"])) # setItem(행,열,데이터)
            self.parent.Danger_wd.setItem(index2, 2, QTableWidgetItem(self.k.acc_portfolio[k]["위험도"])) # 배열과 같이 작동 acc_portfolio[a][b][c]
            index2 += 1

        
    def C_K_F_class(self): # 기관매매추이 <요청> API 호출
        code_list = []
        
        for code in self.k.acc_portfolio.keys():
            code_list.append(code)
        print("계좌 종목 개수 %s" % (code_list))

        #self.parent.progressBar5.setMaximum(len(code_list) - 1) /차 후 설명 드리겠습니다.

        for idx, code in enumerate(code_list):      # code_list 각각에 번호를 붙여줌 (1,547259)(2,875374)...
            #self.parent.progressBar5.setValue(idx) / 차 후 설명드리겠습니다.

            QTest.qWait(1000)

            self.k.kiwoom.dynamicCall("DisconnectRealData(QString)", self.Find_down_Screen)  # 해당 스크린을 끊고 다시 시작

            self.code_in_all = code  # 종목코드 선언 (중간에 코드 정보 받아오기 위해서)
            print("%s / %s : 종목 검사 중 코드이름 : %s." % (idx + 1, len(code_list), self.code_in_all))

            date_today = datetime.today().strftime("%Y%m%d")
            date_prev = datetime.today() - timedelta(20)  # 넉넉히 10일전의 데이터를 받아온다. 또는 20일이상 데이터도 필요 ->20으로 변경함.
            date_prev = date_prev.strftime("%Y%m%d")
            
            print("date_prev: "+str(date_prev)+"date_today: "+str(date_today))

            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시작일자", date_prev)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종료일자", date_today)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기관추정단가구분", "1")
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "외인추정단가구분", "1")
            self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "종목별기관매매추이요청2", "opt10045", "0", self.Find_down_Screen)
            self.detail_account_info_event_loop.exec_()
            
            
            
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): # API를 통한 기관매매추이 <요청>의 결과 값 <수신>

        if sRQName == "종목별기관매매추이요청2": #수신할 데이터 확인sRQName

            cnt2 = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  #GetRepeatCnt로 결과값의 개수 확인
            # 10일치 이상을 하려면 이부분에 10일치 이상데이터 필요
            
            # print("cnt2: "+str(cnt2)) ->> cnt2가 3으로 아래 위험도 비교 시(4개 기준으로 작성된 코드)에 에러발생.
            # 최근 10일 중 영업일이 4일이 안 돼서 발생..

            self.calcul2_data = []
            self.calcul2_data2 = []
            self.calcul2_data3 = []
            self.calcul2_data4 = []

            for i in range(cnt2):  # range(10) ->> 0~9까지 생성
                #GetCommData로 수시
                Kigwan_meme = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "기관일별순매매수량"))  #기관 매매
                Kigwan_meme_ave = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "기관추정평균가"))  #기관 평균가
                Forgin_meme = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "외인일별순매매수량"))  #외인 매매
                Forgin_meme_ave = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "외인추정평균가"))  #외인 평균가
                percentage = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "등락율"))              #등락
                Jongga = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "종가"))                    #종가

                self.calcul2_data.append(int(Kigwan_meme.strip()))
                self.calcul2_data2.append(abs(int(Jongga.strip())))
                self.calcul2_data2.append(abs(int(Kigwan_meme_ave.strip())))
                self.calcul2_data2.append(abs(int(Forgin_meme_ave.strip())))
                self.calcul2_data3.append(int(Forgin_meme.strip()))
                self.calcul2_data4.append(float(percentage.strip()))
                
                # 여기까지 code의 기관일별순매수량, 외국인일별순매수량, 기관/외국인 평균가, 등락률 정보가 나온다.
                # self.kigwan_meme_dong2(self.calcul2_data, self.calcul2_data2[0:3], self.calcul2_data3, self.calcul2_data4)

            self.kigwan_meme_dong2(self.calcul2_data, self.calcul2_data3) # 기관 매매동향을 이용한 위험도 딕셔너리에 추가저장(UPDATE)

            self.detail_account_info_event_loop.exit()
                
                

    def kigwan_meme_dong2(self, a, c):  # a. 기관일별순매수량, b. 종가/기관/외국인 평균가, c. 외국인일별순매수량, d. 등락률

        a = a[0:4] # self.calcul2_data[0],self.calcul2_data[1],self.calcul2_data[2],self.calcul2_data[3]
        c = c[0:4]
        print(a) # 최근4일 기관 매매 수량 
        print(c) # 최근4일 외인 매매 수량 
        # a = sum(a, [])
        # c = sum(c, [])

        print("acc_portfolio[self.code_in_all] 변화 확인(update 전): "+ str(self.k.acc_portfolio[self.code_in_all]))

        if a[0] < 0 and a[1] < 0 and a[2] < 0 and a[3] < 0 and c[0] < 0 and c[1] < 0 and c[2] < 0 and c[3] < 0:
            self.k.acc_portfolio[self.code_in_all].update({"위험도": "손절"})

        elif a[0] < 0 and a[1] < 0 and a[2] < 0 and c[0] < 0 and c[1] < 0 and c[2] < 0:
            self.k.acc_portfolio[self.code_in_all].update({"위험도": "주의"})

        elif a[0] < 0 and a[1] < 0 and c[0] < 0 and c[1] < 0:
            self.k.acc_portfolio[self.code_in_all].update({"위험도": "관심"})

        else:
            self.k.acc_portfolio[self.code_in_all].update({"위험도": "낮음"})

        print("acc_portfolio[self.code_in_all] 변화 확인(update 후): "+ str(self.k.acc_portfolio[self.code_in_all]))
