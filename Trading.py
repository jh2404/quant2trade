import sys                        # system specific parameters and functions : 파이썬 스크립트 관리//현재 디렉토리 확인 가능
import os                         # 고DPI 지원 위해

from PyQt5.QtWidgets import *     # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
from PyQt5.QtCore import *        # Qeventloop/스레드 사용위해


################# 부가 기능 수행(일꾼) #####################################
from kiwoom import Kiwoom          # 키움증권 함수/공용 방 (싱글턴)
from Qthread_1 import Thread1      # 계좌평가잔고내역(평잔) 가져오기
from Qthread_2 import Thread2      # 계좌 관리정보 가져오기
from Qthread_3 import Thread3      # 자동매매 시작


# class Thread1(QThread):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
        
#     self.k = Kiwoon()              # 키움서버 함수 사용을 위한 상속
    
#     self.Acc_Screen = "1000"       # 평잔 받는 스크린
    
#     self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)   # 내가 가진 TR슬롯에 특정 값 던저준다
    
#     self.detail_account_info_event_loop = QEventLoop()        # 계좌 이벤트 루프

#=================== 프로그램 실행 프로그램 =========================#

form_class = uic.loadUiType("TRADER.ui")[0]             # 만들어 놓은 ui 불러오기

class Login_Machnine(QMainWindow, QWidget, form_class):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, *args, **kwargs):                      # Main class의 self를 초기화 한다.

        print("Login Machine 실행합니다.")
        super(Login_Machnine, self).__init__(*args, **kwargs)
        form_class.__init__(self)                            # 상속 받은 from_class를 실행하기 위한 초기값(초기화)
        self.setUI()                                         # UI 초기값 셋업 반드시 필요

        ############################ 초기 셋팅 ##############################
        self.label_11.setText(str("총매입금액"))
        self.label_12.setText(str("총평가금액"))
        self.label_13.setText(str("추정예탁자산"))
        self.label_14.setText(str("총평가손익금액"))
        self.label_15.setText(str("총수익률(%)"))

        self.searchItemTextEdit2.setAlignment(Qt.AlignRight)
        # 종목검색 창 우측정렬

        self.buy_price.setAlignment(Qt.AlignRight) # 우측 정려
        self.buy_price.setDecimals(0) # 소수점 제거 (1이면 xx.x)
        self.n_o_stock.setAlignment(Qt.AlignRight)
        self.n_o_stock.setDecimals(0)
        self.profit_price.setAlignment(Qt.AlignRight)
        self.profit_price.setDecimals(0)
        self.loss_price.setAlignment(Qt.AlignRight)
        self.loss_price.setDecimals(0)

        ############################ ######### ##############################


        self.login_event_loop = QEventLoop()

        ####키움증권 로그인 하기
        self.k = Kiwoom()                     # Kiwoom()을 실행하며 상속 받는다. Kiwoom()은 전지적인 아이다.
        self.set_signal_slot()
        self.signal_login_commConnect()
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다.
        
        self.new_code = ""

        self.call_account.clicked.connect(self.c_acc) # '평잔확인' 버튼 클릭
        
        ################################################################################
        self.acc_manage.clicked.connect(self.a_manage)  # 계좌관리' 버튼 클릭           #  
        self.additemlast.clicked.connect(self.searchItem2) # '종목추가' 버튼 클릭       #   에러처리 필요 구간.. 순서 없이 누르면 에러발생함.
        self.Deletcode.clicked.connect(self.deltecode) # '종목삭제' 버튼 클릭           #
        self.Auto_start.clicked.connect(self.auto) # '자동매매 시작' 버튼 클릭           #
        ################################################################################
        # 텍스트 없이 종목 추가 삭제시 에러발생
        
        
        
        # self.Getanal_code = [] -> load_code 위치로 이동함.
        self.Save_Stock.clicked.connect(self.Save_selected_code)
        self.Del_Stock.clicked.connect(self.delet_code)
        self.Load_Stock.clicked.connect(self.Load_code)
        
        ################################################################################
        # 로드 시 buylast에 중복으로 불러오는 문제 -> 변수를 load_code 함수 내에서 초기화하는 방식으로 해결
        # 세이브 시 기존 파일에 누적 저장하는 문제 -> 고민해봐야 함 // 기존 파일이 있다면 삭제하거나 불러오기 후 추가 가능하도록?
        
        
        
        #self..clicked.connect(self.)  # 버튼 클릭



    def setUI(self):
        self.setupUi(self)                # UI 초기값 셋업

####    CommConnect-------> 서버로 전송(QEventLoop로 중간에 다른 명령이 실행되는 것을 방지)
####    OnEventConnect----> 서버의 응답 값을 받아오는 함수로 전달 받은 값을 ()괄호 안으로 넣어줌
    
    def set_signal_slot(self):
        self.k.kiwoom.OnEventConnect.connect(self.login_slot)
        
    def signal_login_commConnect(self):
        self.k.kiwoom.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()
        
    def login_slot(self, errCode):
        if errCode == 0:
            print("로그인 성공")
            self.statusbar.showMessage("로그인 성공")
            self.get_account_info()
        
        elif errCode == 100:
            print("사용자 정보교환 실패")
            
        elif errCode == 101:
            print("서버접속 실패")
            
        elif errCode == 102:
            print("버전처리 실패")
        
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.k.kiwoom.dynamicCall("GetLoginInfo(String)","ACCNO") #self.k 메타클래스 기반 싱글턴 #kiwoom.dynamicCall 키움서버에 특정정보 요청 시 사용하는 함수
        # 예를 들어 보유계좌 개수가 알고 싶다면 self.k.kiwoom.dynamicCall("GetLoginInfo(string)","ACCOUNT_CNT")
        
        for n in account_list.split(';'):
            self.accComboBox.addItem(n)

    def c_acc(self):
        print("선택 계좌 정보 가져오기")
        ##### 1번 쓰레드 실행
        h1 = Thread1(self)
        h1.start()

    def a_manage(self):
        print("계좌관리 정보 호출")
        ##### 2번 쓰레드 실행
        h2 = Thread2(self)
        h2.start()

    def auto(self):
        print("자동매매 시작")
        ##### 3번 쓰레드 실행
        h3 = Thread3(self)
        h3.start()

    def searchItem2(self):
        itemName = self.searchItemTextEdit2.toPlainText()
        if itemName !="":
            for code in self.k.All_Stock_Code.keys():
                if itemName == self.k.All_Stock_Code[code]["종목명"]:
                    self.new_code = code
                
        column_head = ["종목코드", "종목명", "현재가", "신용비율", "매수가", "매수수량", "익절가", "손절가"]
        colCount = len(column_head)
        row_count = self.buylast.rowCount() # 실제 row개수를 반환
        
        #print("row_count: " + str(self.buylast.rowCount())) # m
        
        self.buylast.setColumnCount(colCount)  # 열 개수 지정.
        self.buylast.setRowCount(row_count+1)  # 행 개수를 불러와 변수에 저장해두고 행의 크기를 한칸만큼 늘린다.(늘린다->행추가한다)

        #print("row_count: " + str(self.buylast.rowCount())) # m+1
        # 행 개수를 불러와 변수에 저장해두고 행의 크기를 한칸만큼 늘린다.(행추가 ->> searchItem이 사실상 리스트 추가의 기능이기 때문)
        # colum_haed가 한 행을 잡아 먹는다. 실제 입력 되는 값은 1행 부터이다. 실제 row보다 하나 더 필요(colum_haed를 위해)
        
        #print("setHorizontalHeaderLabels 이전" + str(self.buylast.rowCount()))# setHorizontalHeaderLabels 이전 -> n
        
        self.buylast.setHorizontalHeaderLabels(column_head)  # 행의 이름 삽입
        
        #print("setHorizontalHeaderLabels 이후" + str(self.buylast.rowCount()))# setHorizontalHeaderLabels 이후 -> n (여전히 n) 열이름 설정때문에 행(row_Count)이 변하는 게 아님.
        # row_count 변수는 여전히 +1이 안된 값을 가짐. ->> row_count 변수의 값을 행추가 과정 (self.buylast.setRowCount(row_count+1))
        # 이후에 다시 받아 사용하면 searchItem2 와 trdata_slot에서의 변수 사용방법을 같게 만들수도..
        
        self.buylast.setItem(row_count, 0, QTableWidgetItem(str(self.new_code))) # (row_count==행)실제 입력값은 1행부터이나 0부터 들어가야 된다.
        self.buylast.setItem(row_count, 1, QTableWidgetItem(str(itemName))) 
        # 위 내용의 부연: 테이블 위젯을 그릴 때에는 각 열의 이름인 column_head를 위해 하나더 그리지만 입력(배열처럼 생각)에서는 row_count 0이 첫째 로 입력 받는 공간임
        
        # 2,3이 없는 이유??
        # row_count,[2:3]의 값은 trdata_slot에서 받은 값으로 입력해줌(row_count-1,[2:3])
        # 2->현재가 3->신용비율
        self.buylast.setItem(row_count, 4, QTableWidgetItem(str(self.buy_price.value()))) #TextEdit변수명.toPainText() ->> DoubleSpinBox변수명.value()
        self.buylast.setItem(row_count, 5, QTableWidgetItem(str(self.n_o_stock.value())))
        self.buylast.setItem(row_count, 6, QTableWidgetItem(str(self.profit_price.value())))
        self.buylast.setItem(row_count, 7, QTableWidgetItem(str(self.loss_price.value())))

        
        #self.searchItemTextEdit2.setAlignment(Qt.AlignRight) 
        # 이 위치에 넣으면 버튼 눌러야 오른쪽으로 정렬됨. 처음부터 정렬하려면 위쪽에 정의 필요
        
        self.getItemInfo(self.new_code)
        

    def getItemInfo(self, new_code):
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", new_code)
        self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보요청", "opt10001", 0, "100")


#######  buylast 화면에 뿌려주는 방식 1. searchItem2이후 trdata_slot 2. Load_code
#######  두 방식에 모두 정렬 코드를 추가하면 정렬 가능할듯???????????
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sTrCode == "opt10001":
            if sRQName == "주식기본정보요청": # 계좌 정보 불러오기 안하고 실행시 에러...->> 해결 필요.
                currentPrice = abs(int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "현재가")))
                D_R = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "신용비율")).strip()
                row_count = self.buylast.rowCount()
                self.buylast.setItem(row_count - 1, 2, QTableWidgetItem(str(currentPrice))) 
                # 실제 buylast에서는 2행(rowcount) BUT!! setItem(입력)에서는 1행은 무시되고 그 다음 진짜 값이 있는 곳이 1행임.
                # 위와 같은 현상이 발생하는 이유??
                # ->> 위쪽의 searchItem2 함수에서 self.buylast.rowCount()를 호출할 때와 trdata_slot에서 호출할 때의 상황이 변함
                #     위에서는 rowCount() 호출 이후에 setHorizontalHeaderLabels(column_head)를 설정해 행이 하나씩 밀림 and SO.. 이 이후에 같은 행을 받으려면 -1을 해야 같은 행임.
                self.buylast.setItem(row_count - 1, 3, QTableWidgetItem(str(D_R)))
                
                print("trdata_slot에서 row_Count" + str(self.buylast.rowCount()))# 여기서는 2... n+1 이다. 이유: 
    def deltecode(self):
        x = self.buylast.selectedIndexes()
        self.buylast.removeRow(x[0].row())

    def Save_selected_code(self):
        for row in range(self.buylast.rowCount()):
            code_n = self.buylast.item(row, 0).text()
            name = self.buylast.item(row, 1).text().strip() #공백제거
            price = self.buylast.item(row, 2).text()
            dept = self.buylast.item(row, 3).text()
            mesu = self.buylast.item(row, 4).text()
            n_o_stock = self.buylast.item(row, 5).text()
            profit = self.buylast.item(row, 6).text()
            loss = self.buylast.item(row, 7).text()
## 참고 ## column_head = ["종목코드", "종목명", "현재가", "신용비율", "매수가", "매수수량", "익절가", "손절가"]


            f = open("dist/Selected_Code.txt", "a", encoding = "utf-8")
            f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (code_n, name, price, dept, mesu, n_o_stock, profit, loss))
            f.close()
            
            
    def Load_code(self):
        self.Getanal_code = []  # 초기화
        
        if os.path.exists("dist/Selected_Code.txt"):
            f = open("dist/Selected_Code.txt", "r", encoding = "utf-8")
            lines = f.readlines()
            
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
                    
                    
                    self.Getanal_code.append([t_code, t_name, curren_price, dept, mesu, n_o_stock, profit, loss])
            f.close()
            
        column_head = ["종목코드", "종목명", "현재가", "신용비율", "매수가", "매수수량", "익절가", "손절가"]
        colCount = len(column_head)
        rowCount = len(self.Getanal_code)
        
        self.buylast.setColumnCount(colCount)
        self.buylast.setRowCount(rowCount)
        self.buylast.setHorizontalHeaderLabels(column_head)
        self.buylast.setSelectionMode(QAbstractItemView.SingleSelection)
        
        for index in range(rowCount):
            self.buylast.setItem(index, 0, QTableWidgetItem(str(self.Getanal_code[index][0])))
            self.buylast.setItem(index, 1, QTableWidgetItem(str(self.Getanal_code[index][1])))
            self.buylast.setItem(index, 2, QTableWidgetItem(str(self.Getanal_code[index][2])))
            self.buylast.setItem(index, 3, QTableWidgetItem(str(self.Getanal_code[index][3])))
            self.buylast.setItem(index, 4, QTableWidgetItem(str(self.Getanal_code[index][4])))
            self.buylast.setItem(index, 5, QTableWidgetItem(str(self.Getanal_code[index][5])))
            self.buylast.setItem(index, 6, QTableWidgetItem(str(self.Getanal_code[index][6])))
            self.buylast.setItem(index, 7, QTableWidgetItem(str(self.Getanal_code[index][7])))
# self.Getanal_code.append([t_code, t_name, curren_price, dept, mesu, n_o_stock, profit, loss]) /// 이 코드(def Load_code) 내의 append로 추가된 데이터들을 접근
            
            
    def delet_code(self):
        if os.path.exists("dist/Selected_Code.txt"):
            os.remove("dist/Selected_Code.txt")


#======================================================================#
#######MAIN#######
if __name__=='__main__':             # import된 것들을 실행시키지 않고 __main__에서 실행하는 것만 실행 시킨다.
                                     # 즉 import된 다른 함수의 코드를 이 화면에서 실행시키지 않겠다는 의미이다.

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  #고해상도 대응
    app = QApplication(sys.argv)     # PyQt5로 실행할 파일명을 자동으로 설정, PyQt5에서 자동으로 프로그램 실행
    #app.setAttribute(Qt.AA_EnableHighDpiScaling)     #고해상도 대응
    
    CH = Login_Machnine()            # Main 클래스 myApp으로 인스턴스화
    CH.show()                        # myApp에 있는 ui를 실행한다.
    app.exec_()                      # 이벤트 루프``