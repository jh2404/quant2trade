from PyQt5.QtWidgets import *                 # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget) # ActiveX 컨트롤사용하는 함수: 외부 라이브러리 or 컴포넌트를 사용하기 위해(키움증권 클래스 사용) 
from PyQt5Singleton import Singleton

class Kiwoom(QWidget, metaclass=Singleton):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, parent=None, **kwargs):     # Main class의 self를 초기화 한다.
        
        print("로그인 프로그램을 실행합니다.")

        super().__init__(parent, **kwargs)

        ################ 로그인 관련 정보

        self.kiwoom = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')       # CLSID
        
        self.All_Stock_Code = {}            # 코스피, 코스닥 전체 코드넘버 입력
        self.acc_portfolio = {}             # 계좌에 들어있는 종목의 코드, 수익률 등등 입력
        self.portfolio_stock_dict = {}      # 포트폴리오에 들어있는 종목의 코드, 수익률 등등 입력되어 있는 딕셔너리
        
        self.today_meme = []                # 금일 매매하는 종목에 대한 정보를 담는다.
        self.not_account_stock_dict = {}    # 미체결 잔고 딕셔너리
        
        # [] : 리스트, {} : 딕셔너리, () : 튜플
        # 리스트 : 순서가 있는 객체의 집합, 딕셔너리 : 순서가 없는 객체의 집합, 튜플 : 리스트와 같지만 수정이 불가능하다.
        # 딕셔너리는 키와 값으로 이루어져 있다. 키는 중복이 불가능하다.
        # 딕셔너리는 {키1:값1, 키2:값2, 키3:값3} 형태로 만들어진다.
        #
        
        ################# 오늘 산 잔고
        
        self.jango_dict = {}                # 잔고 딕셔너리
        self.buy_jogon = {}                 # 매수 조건 딕셔너리
