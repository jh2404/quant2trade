import os
from PyQt5.QtCore import *           # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from kiwoom import Kiwoom            # 로그인을 위한 클래스
from kiwoomType import *
from PyQt5.QtWidgets import *      #PyQt import

class Thread3(QThread):
    def __init__(self, parent):   # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)  # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent      # 부모의 윈도우를 사용하기 위한 조건


        ################## 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.k = Kiwoom()
        ##################

        ################## 사용되는 변수


        ###### 슬롯
        ##self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다. 여기선 OnReceiveRealData로 사용
        ###### EventLoop
        #자동매매의 경우 이벤트 루프가 필요할지 고민이 필요함.
        #self.detail_account_info_event_loop = QEventLoop()  # 계좌 이벤트루프
        
        #Thread 끼리는 통신이 불가하기에 gui에서 account 정보 가져옴
        account = self.parent.accComboBox.currentText()
        self.account_num = account
# 계좌번호 가져오는 부분은 Qthread_3 분리 시 로그인 후 계좌번호를 가져오는 함수로 교체된다

        self.Load_code() # 파일로부터 매수 종목/금액/수량 가져오기
        
        self.orderitmelist_1 = [] # 중복 매수 금지
        self.orderitmelist_2 = [] # 중복 익절 금지
        self.orderitmelist_3 = [] # 중복 손절 금지
        self.orderitmelist_4 = [] # 중복 재매수 금지
        self.cancel_the_order = []

        
        self.realType = RealType() # 실시간 FID 값들을 모아둔 RealType을 이용해 realType 객체 생성
        


        ######################################################################
        ###### 등록된 계좌 전체 해제하기(작동 정지 되었을 때 등록 정보를 다 끊어야 한다.)
        # 새 정보를 요청하기 전 이전에 있을지 모를 요청정보를 모두 삭제한다.
        self.k.kiwoom.dynamicCall("SetRealRemove(QString, QString)", ["ALL", "ALL"])
        ######################################################################

        ######################################################################
        ###### 선정된 종목 등록하기 : 키움서버에 리얼 데이터 등록하기

        self.screen_num = 5000

        for code in self.k.portfolio_stock_dict.keys():  # 포트폴리오에 저장된 코드들을 실시간 등록
            fids = self.realType.REALTYPE['주식체결']['체결시간']  # 주식체결에 대한 모든 데이터를 로드할 수 있다.
        
        ### kiwoomType.py ###    
        # REALTYPE = {

        #     '주식체결': {
        #         '체결시간': 20,
        #     }
        # }
        # 여기서는 체결시간만 요청하지만 ->> 넘겨 받는 데이터에는 모든 데이터가 포함된다.(여러가지를 요청할 필요 없다)
            self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_num, code, fids, "1")  # 실시간 데이터를 받아오기 위해 각 코드들을 서버에 등록(틱 변화가 있으면 데이터 송신)
            self.screen_num += 1

        #   [SetRealReg() 함수]
        
        #   SetRealReg(
        #   BSTR strScreenNo,   // 화면번호
        #   BSTR strCodeList,   // 종목코드 리스트
        #   BSTR strFidList,  // 실시간 FID리스트
        #   BSTR strOptType   // 실시간 등록 타입, 0또는 1
        #   )
        
        #   종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.
        #   한번에 등록가능한 종목과 FID갯수는 100종목, 100개 입니다.
        #   실시간 등록타입을 0으로 설정하면 등록한 종목들은 실시간 해지되고 등록한 종목만 실시간 시세가 등록됩니다.
        #   실시간 등록타입을 1로 설정하면 먼저 등록한 종목들과 함께 실시간 시세가 등록됩니다

        #   OpenAPI.SetRealReg(_T("0150"), _T("039490"), _T("9001;302;10;11;25;12;13"), "0");  // 039490종목만 실시간 등록
        #   OpenAPI.SetRealReg(_T("0150"), _T("000660"), _T("9001;302;10;11;25;12;13"), "1");  // 000660 종목을 실시간 추가등록


        # print("실시간 등록 : %s, 스크린번호 : %s, FID  번호 : %s" % (code, screen_num, fids))
        print("종목등록 완료")
        print(self.k.portfolio_stock_dict.keys())


        ######################################################################
        ###### 현재 장 상태 알아보기 (장 시작 / 장 마감 등)
        self.screen_start_stop_real = "300"       # 장시 시작 전/후 상태 확인용 스크린 번호
        self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")  # 장의 시작인지, 장 외인지등에 대한 정보 수신

        ###### 실시간 슬롯 (데이터를 받아오는 슬롯을 설정한다)
        self.k.kiwoom.OnReceiveRealData.connect(self.realdata_slot)   # 실시간 데이터를 받아오는 곳
        # 실시간 데이터의 호출은 누가??? 언제???

        self.k.kiwoom.OnReceiveChejanData.connect(self.chejan_slot)   # (주문접수, 체결통보)=0, (잔고변경) = 1 데이터 전송



    def Load_code(self):
        if os.path.exists("dist/Selected_Code.txt"):
            f = open("dist/Selected_Code.txt", "r", encoding="utf-8")
            lines = f.readlines()
            screen = 4000
            
            # New set to keep track of codes from the Selected_Code.txt
            file_codes = set()
            
            for line in lines:
                if line != "":
                    ls = line.split("\t")  
                    t_code = ls[0]
                    t_name = ls[1]
                    curren_price = ls[2]
                    dept = ls[3]
                    mesu = ls[4]
                    n_o_stock = ls[5]
                    profit = ls[6]
                    loss = ls[7].split("\n")[0]

                    file_codes.add(t_code)

                    self.k.portfolio_stock_dict.update({t_code: {"종목명": t_name}})
                    #딕셔너리 생성 ->> "{547259:{종목명:삼성전자}}"
                    self.k.portfolio_stock_dict[t_code].update({"현재가": int(curren_price)})
                    #딕셔너리 생성 ->> "{547259:{종목명:삼성전자, 현재가:70000}}"...
                    self.k.portfolio_stock_dict[t_code].update({"신용비율": dept})
                    self.k.portfolio_stock_dict[t_code].update({"매수가": int(mesu)}) # qtdesigner에서 소수점 있는 상태로 받아오면 에러 발생
                    # int(float(mesu))로 수정이 필요함. OR qtdesigner에서 소수점 없는 상태로 받아오기
                    self.k.portfolio_stock_dict[t_code].update({"매수수량": int(n_o_stock)})
                    self.k.portfolio_stock_dict[t_code].update({"익절가": int(profit)})
                    self.k.portfolio_stock_dict[t_code].update({"손절가": int(loss)})
                    self.k.portfolio_stock_dict[t_code].update({"주문용스크린번호": screen})  # 아래 내용을 업데이트
                    screen += 1
            # Synchronization logic
            for code in list(self.k.portfolio_stock_dict.keys()):
                if code not in file_codes:
                    del self.k.portfolio_stock_dict[code]
            f.close()
            print(self.k.portfolio_stock_dict)






        
    # def Load_code(self):
    #     if os.path.exists("dist/Selected_Code.txt"):
    #         f = open("dist/Selected_Code.txt", "r", encoding="utf-8")
    #         lines = f.readlines()
    #         screen = 4000
            
    #         for line in lines:
    #             if line != "":
    #                 ls = line.split("\t")  # \t(tap)로 구분을 지어 놓는다.
    #                 t_code = ls[0]
    #                 t_name = ls[1]
    #                 curren_price = ls[2]
    #                 dept = ls[3]
    #                 mesu = ls[4]
    #                 n_o_stock = ls[5]
    #                 profit = ls[6]
    #                 loss = ls[7].split("\n")[0]

    #                 self.k.portfolio_stock_dict.update({t_code: {"종목명": t_name}})
    #                 #딕셔너리 생성 ->> "{547259:{종목명:삼성전자}}"
    #                 self.k.portfolio_stock_dict[t_code].update({"현재가": int(curren_price)})
    #                 #딕셔너리 생성 ->> "{547259:{종목명:삼성전자, 현재가:70000}}"...
    #                 self.k.portfolio_stock_dict[t_code].update({"신용비율": dept})
    #                 self.k.portfolio_stock_dict[t_code].update({"매수가": int(mesu)}) # qtdesigner에서 소수점 있는 상태로 받아오면 에러 발생
    #                 # int(float(mesu))로 수정이 필요함. OR qtdesigner에서 소수점 없는 상태로 받아오기
    #                 self.k.portfolio_stock_dict[t_code].update({"매수수량": int(n_o_stock)})
    #                 self.k.portfolio_stock_dict[t_code].update({"익절가": int(profit)})
    #                 self.k.portfolio_stock_dict[t_code].update({"손절가": int(loss)})
    #                 self.k.portfolio_stock_dict[t_code].update({"주문용스크린번호": screen})  # 아래 내용을 업데이트
    #                 screen += 1
    #         f.close()
    #         print(self.k.portfolio_stock_dict)
            
    def realdata_slot(self, sCode, sRealType, sRealData): 
    # 1. API를 통한 'RealData' <요청>의 결과 값 <수신>
    # 2. 실시간시세 데이터가 수신될때마다 종목단위로 발생됩니다.
    # sCode:종목코드, sRealType:실시간타입(FID), sRealData:실시간 데이터 전문
    # SetRealReg()함수로 등록한 실시간 데이터도 이 이벤트로 전달됩니다.
    # GetCommRealData()함수를 이용해서 수신된 데이터를 얻을수 있습니다.

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']

            # 실시간시세 데이터 수신 이벤트인 OnReceiveRealData() 가 발생될때 실시간데이터를 얻어오는 함수
            value = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == '0':
                print("장 시작 전")

            elif value == '3':
                print("장 시작")

            elif value == '2':
                print("장 종료, 동시호가로 넘어감")

            elif value == '4':
                print("장 마감했습니다.")
                
            # market_code = {'0': '장시작전', '2': '장마감전동시호가', '3': '장시작', '4': '장종료-예상지수종료',
            #                '8': '장마감', '9': '장종료-시간외종료', 'a': '시간외종가매매시작', 'b': '시간외종가매매종료',
            #                'c': '시간외단일가매매시작', 'd':'시간외단일가매매종료',
            #                's': '선옵장마감전동시호가시작', 'e': '선옵장마감전동시호가종료'}
            

        elif sRealType == "주식체결" and sCode in self.k.portfolio_stock_dict:


            fid1 = self.realType.REALTYPE[sRealType]['체결시간']  # 체결시간은 string으로 나온다. HHMMSS
            a = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid1)

            fid2 = self.realType.REALTYPE[sRealType]['현재가']  # 현재가는 +/-로 나온다.
            b = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid2)
            b = abs(int(b))

            fid3 = self.realType.REALTYPE[sRealType]['전일대비']  # 전달 대비 오르거나/내린 가격
            c = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid3)
            c = abs(int(c))

            fid4 = self.realType.REALTYPE[sRealType]['등락율']  # 전달 대비 오르거나/내린 퍼센테이지
            d = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid4)
            d = float(d)

            fid5 = self.realType.REALTYPE[sRealType]['(최우선)매도호가']  # 매도쪽에 첫번재 부분(시장가)
            e = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid5)
            e = abs(int(e))

            fid6 = self.realType.REALTYPE[sRealType]['(최우선)매수호가']  # 매수쪽에 첫번재 부분(시장가)
            f = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid6)
            f = abs(int(f))

            fid7 = self.realType.REALTYPE[sRealType]['거래량']  # 틱봉의 현재 거래량 (아주 작으 단위)
            g = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid7)
            g = abs(int(g))

            fid8 = self.realType.REALTYPE[sRealType]['누적거래량']
            h = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid8)
            h = abs(int(h))

            fid9 = self.realType.REALTYPE[sRealType]['고가']  # 오늘자 재일 높은 가격
            i = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid9)
            i = abs(int(i))

            fid10 = self.realType.REALTYPE[sRealType]['시가']  # 시가
            j = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid10)
            j = abs(int(j))

            fid11 = self.realType.REALTYPE[sRealType]['저가']  # 전체 재일 낮은 가격
            k = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid11)
            k = abs(int(k))

            fid12 = self.realType.REALTYPE[sRealType]['거래회전율']  # 누적 거래회전율
            l = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid12)
            l = abs(float(l))

            if sCode not in self.k.portfolio_stock_dict:           # 만약 서버에 등록된 코드가 포트폴리오에 없다면 코드를 등록
                self.k.portfolio_stock_dict.update({sCode: {}})

            # 포트폴리오 종목코드마다 아래 실시간 데이터를 입력
            self.k.portfolio_stock_dict[sCode].update({"채결시간": a})       # 아래 내용을 업데이트
            self.k.portfolio_stock_dict[sCode].update({"현재가": b})
            self.k.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.k.portfolio_stock_dict[sCode].update({"등락율": d})
            self.k.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.k.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.k.portfolio_stock_dict[sCode].update({"거래량": g})
            self.k.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.k.portfolio_stock_dict[sCode].update({"고가": i})
            self.k.portfolio_stock_dict[sCode].update({"시가": j})
            self.k.portfolio_stock_dict[sCode].update({"저가": k})
            self.k.portfolio_stock_dict[sCode].update({"거래회전율": l})



            ###############################################################
            ############# 실시간을 위한 조건문 구성하기 ########################
            ###############################################################


            #1. 매수 알고리즘 가동

            #1차#############################################################################################
            if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["매수가"]:
                if sCode not in self.orderitmelist_1:

                    wa = []
                    wa.append(sCode)

                    if len(wa) > 1:
                        wa.clear()
                        pass
                    else:
                        print("매수 시작 %s" % sCode)

                        self.orderitmelist_1.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                        order_success1 = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)", 
                                                                    ["신규매수", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode, 
                                                                    self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                                                    self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files이라는 파이썬 패키지 폴더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1매수정보", self.k.portfolio_stock_dict[sCode]["종목명"], b, self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                        if order_success1 == 0:
                            print("최우선매수호가로 주문 전달 성공")
                        else:
                            print("최우선매수호가로 주문 전달 실패")
                            
            #2. 매도 알고리즘 가동

            #1차 익절 #############################################################################################
            if self.k.portfolio_stock_dict[sCode]["현재가"] >= self.k.portfolio_stock_dict[sCode]["익절가"]:
                if sCode not in self.orderitmelist_2:

                    wa = []
                    wa.append(sCode)

                    if len(wa) > 1: # 중복 매도 금지 코드 self.orderitemlist_2를 뚫은 sCode가 2개 이상이면 중복 매도가 발생할 수 있으므로 매도 금지
                        wa.clear()
                        pass        # 차라리 다음 틱에 매도가 되도록 한다.(오 매도 보단 매도를 건너뛰는게 낫다.)
                    else:
                        print("매도 시작 %s" % sCode)
                        
                        self.orderitmelist_2.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                        order_success2 = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)", 
                                                                    ["신규익절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode, 
                                                                    self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                                                    self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        
                        wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files이라는 파이썬 패키지 폴더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1익절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b, self.k.portfolio_stock_dict[sCode]["채결시간"]))
                        wf2.close()
                        
                        if order_success2 == 0:
                            print("익절가로 주문 전달 성공")
                        else:
                            print("익절가로 주문 전달 실패")
                        
                            
            #1차 손절 #############################################################################################
            if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["손절가"]:
                if sCode not in self.orderitmelist_3:

                    wa = []
                    wa.append(sCode)

                    if len(wa) > 1: # 중복 매도 금지 코드 self.orderitemlist_3를 뚫은 sCode가 2개 이상이면 중복 매도가 발생할 수 있으므로 매도 금지
                        wa.clear()
                        pass
                    else:
                        print("손절 시작 %s" % sCode)
                        
                        self.orderitmelist_3.append(sCode)
                        order_success3 = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)", 
                                                                    ["신규손절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode, 
                                                                    self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                                                    self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        
                        wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1손절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b, self.k.portfolio_stock_dict[sCode]["채결시간"]))
                        wf2.close()
                        
                        if order_success3 == 0:
                            print("손절가로 주문 전달 성공")
                        else:
                            print("손절가로 주문 전달 실패")

            #미체결 잔고 매수/매도 취소 #############################################################################################
            not_meme_list = list(self.k.not_account_stock_dict)  # 체결하지 않은 종목들을 실제 미체결 잔고에서 받아온다.
            if len(self.k.not_account_stock_dict) > 0:

                for order_num in not_meme_list:  # not_meme_listnot_meme_list에는 주문번호가 들어가 있다.

                    code = self.k.not_account_stock_dict[order_num]["종목코드"]
                    meme_price = self.k.not_account_stock_dict[order_num]['주문가격']
                    not_quantity = self.k.not_account_stock_dict[order_num]['미체결수량']
                    order_gubun = self.k.not_account_stock_dict[order_num]['주문구분']

                    ##### 매수에 대한 취소 주문 : 주문가격이 최우선 매수호가보다 작을 경우

                    if order_gubun == "매수" and not_quantity > 0 and meme_price < self.k.portfolio_stock_dict[sCode]["현재가"]:

                        order_success = self.k.kiwoom.dynamicCall(
                            "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                            ["매수취소", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 3, code, 0, 0,
                            self.realType.SENDTYPE['거래구분']['지정가'], order_num])  # order_num 은 어떤 주문을 취소할 것인가.

                        if order_success == 0:
                            print("%s 매수취소 전달 성공" % code)  # 체결잔고에서  del을 했기 때문에 여기서 하지 않는다.
                            self.cancel_the_order.append(code)  # 차 후 재매수를 위해 필요함
                        else:
                            print("%s 매수취소 전달 실패" % code)

                        wf2 = open("dist/chiso_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("매수취소", self.k.portfolio_stock_dict[sCode]["종목명"], not_quantity, self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                    elif not_quantity == 0:
                        del self.k.not_account_stock_dict[order_num]


                    ##### 매도에 대한 취소 주문 : 주문가격이 최우선매도호가보다 클결우

                    elif order_gubun == "매도" and not_quantity > 0 and self.k.portfolio_stock_dict[sCode]["현재가"] < meme_price:

                        order_success = self.k.kiwoom.dynamicCall(
                            "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                            ["매도취소", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 4, code, 0, 0,
                            self.realType.SENDTYPE['거래구분']['지정가'], order_num])  # order_num 은 어떤 주문을 취소할 것인가.

                        wf2 = open("dist/chiso_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("매도취소", self.k.portfolio_stock_dict[sCode]["종목명"], not_quantity,
                                                        self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                        if order_success == 0:
                            print("%s 매도취소 전달 성공" % code)  # 체결잔고에서  del을 했기 때문에 여기서 하지 않는다.
                            self.cancel_the_order.append(code)  # 차 후 재매수를 위해 필요함

                        else:
                            print("%s 매도취소 전달 실패" % code)

                    elif not_quantity == 0:
                        del self.k.not_account_stock_dict[order_num]



            ########################
            # 5. 재 매수 알고리즘 : 현재가가 매수 되지 못하였을 경우를 대비하여 재 매수 알고리즘 가동
            ########################
            elif sCode in self.cancel_the_order:
                # 재매수#############################################################################################
                if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["매수가"]:
                    if sCode not in self.orderitmelist_4:
                        wa = []
                        wa.append(sCode)

                        if len(wa) > 1:
                            wa.clear()
                            pass
                        else:
                            print("재매수 시작 %s" % sCode)

                            self.orderitmelist_4.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                            order_success3 = self.k.kiwoom.dynamicCall(
                                "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                ["신규매수", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode,
                                self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                            wf2.write("%s\t%s\t%s\t%s\n" % ("재매수정보", self.k.portfolio_stock_dict[sCode]["종목명"], b,
                                                            self.k.portfolio_stock_dict[sCode][
                                                                "채결시간"]))  # t는 tap을 의미한다.
                            wf2.close()
                            if order_success3 == 0:
                                print("재매수 주문 전달 성공")
                            else:
                                print("재매수 주문 전달 실패")



    def chejan_slot(self, sGubun, nItemCnt, sFIdList):   # 주문전송 후 주문접수, 체결통보, 잔고통보를 수신

        if sGubun == "0":
            print("매수/매도 중입니다. 미체결 잔고 업데이트")
        else:
            print("미체결잔고 해결로 실제 잔고 업데이트")

        if int(sGubun) == 0:   # 주문전송 후 미체결 되었을 때 아래와 같은 연산을 해 준다.
            account_num = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]  # [A203042]
            stock_name = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()  # 혹시라도 공백이 있을 까봐
            origin_order_number = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])  # 원주문번호가 없으면 0000000이다
            order_number = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])
            order_status = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])  # 접수/확인/체결 정보
            order_quan = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])
            order_quan = int(order_quan)
            order_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])
            order_price = int(order_price)
            not_chegual_quan = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])
            not_chegual_quan = int(not_chegual_quan)
            order_gubun = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])  # 정정 등, 부호가 나오기 때문에 잡아줘야 된다.
            order_gubun = order_gubun.lstrip('+').lstrip('-')
            order_gubun = order_gubun.strip()
            chegual_time_str = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])  # '151028'
            chegual_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])

            if chegual_price == '':
                chegual_price = 0  # 숫자로 할당
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])

            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            current_price = abs(int(current_price))
            first_sell_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if order_number not in self.k.not_account_stock_dict.keys(): # 새 주문의 미체결 주문번호가 not_account_stock_dict에 없다면 추가
                self.k.not_account_stock_dict.update({order_number: {}})
                
            self.k.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.k.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.k.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.k.not_account_stock_dict[order_number].update({"주문상태": order_status})
            self.k.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.k.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.k.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            self.k.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.k.not_account_stock_dict[order_number].update({"체결양": chegual_quantity})
            self.k.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            self.k.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.k.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.k.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.k.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.k.not_account_stock_dict[order_number].update({"(최우선)매수호가": first_buy_price})
            

            column_head = ["종목코드", "종목명", "주문번호", "주문상태", "주문수량", "주문가격", "미체결수량"]
            colCount = len(column_head)
            rowCount = (len(self.k.not_account_stock_dict))
            self.parent.not_account.setColumnCount(colCount)                 # 행 갯수
            self.parent.not_account.setRowCount(rowCount)                    # 열 갯수 (종목 수)
            self.parent.not_account.setHorizontalHeaderLabels(column_head)   # 행의 이름 삽입

            for index in range(rowCount):
                self.parent.not_account.setItem(index, 0, QTableWidgetItem(str(sCode)))
                self.parent.not_account.setItem(index, 1, QTableWidgetItem(str(stock_name)))
                self.parent.not_account.setItem(index, 2, QTableWidgetItem(str(format(order_number))))
                self.parent.not_account.setItem(index, 3, QTableWidgetItem(str(format(order_status))))
                self.parent.not_account.setItem(index, 4, QTableWidgetItem(str(format(order_quan, ","))))
                self.parent.not_account.setItem(index, 5, QTableWidgetItem(str(format(order_price, ","))))
                self.parent.not_account.setItem(index, 6, QTableWidgetItem(str(format(not_chegual_quan, ","))))

            print("미체결잔고 종목 추가 %s 수량 %s" % (self.k.not_account_stock_dict[order_number]["종목명"], self.k.not_account_stock_dict[order_number]["미체결수량"]))
            


        elif int(sGubun) == 1:
            account_num = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]  # [A203042]
            stock_name = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()  # 혹시라도 공백이 있을 까봐
            current_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])  # 원주문번호가 없으면 0000000이다
            current_price = abs(int(current_price))
            stock_quan = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)
            like_quan = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)
            buy_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))
            total_buy_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)
            meme_gubun = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]
            first_sell_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = int(first_sell_price)
            first_buy_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = int(first_buy_price)
            first_buy_price1 = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['예수금'])
            first_buy_price1 = int(first_buy_price1)
            ##### 계좌평가 잔고내역의 종목이 매도되었을 경우 jango_dict에는 존재하지 않기 때문에
            if sCode not in self.k.jango_dict.keys():
                self.k.jango_dict.update({sCode: {}})
            self.k.jango_dict[sCode].update({"현재가": current_price})
            self.k.jango_dict[sCode].update({"종목코드": sCode})
            self.k.jango_dict[sCode].update({"종목명": stock_name})
            self.k.jango_dict[sCode].update({"보유수량": stock_quan})
            self.k.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.k.jango_dict[sCode].update({"매입단가": buy_price})
            self.k.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.k.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.k.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.k.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})
            if sCode in self.k.acc_portfolio.keys() and stock_quan == 0:
                del self.k.acc_portfolio[sCode]
                #self.k.acc_portfolio[sCode]['매매가능수량'] = 0






