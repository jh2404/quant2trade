
from PyQt5.QtWidgets import *                 # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget) # ActiveX 컨트롤사용하는 함수: 외부 라이브러리 or 컴포넌트를 사용하기 위해(키움증권 클래스 사용) 
from PyQt5Singleton import Singleton

class Kiwoom(QWidget, metaclass=Singleton):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, parent=None, **kwargs):                    # Main class의 self를 초기화 한다.

        print("로그인 프로그램을 실행합니다.")

        super().__init__(parent, **kwargs)

        ################ 로그인 관련 정보

        self.kiwoom = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')       # CLSID