# -*- coding: utf-8 -*-
import time
import socket
import re
import subprocess
import os
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
import pathlib
import json
import random
import threading
import base64
import platform
import getpass
from abc import ABC, abstractmethod
import serial
import typing
import traceback

IMP_ERR = None
try:
    from cryptography.fernet import Fernet
    from cryptography.fernet import InvalidToken
    import paramiko
    from antlr4.InputStream import InputStream
    from antlr4.CommonTokenStream import CommonTokenStream
    from antlr4.tree.Tree import ParseTreeVisitor
    from antlr4.error.ErrorListener import ErrorListener
    import pexpect
    import uptime
    from .ttl_parser_lexer import TtlParserLexer
    from .ttl_parser_parser import TtlParserParser
    from .version import VERSION
except ImportError as ex:
    class ParseTreeVisitor():
        pass
    IMP_ERR = ex


class MyFindfirst:
    ''' find first handle class '''

    def __init__(self, target):
        target = target.replace('.', '\\.').replace('*', '.*')
        self.my_list = []
        for f in os.listdir(os.getcwd()):
            # print(f"MyFindfirst1 {target} {f}")
            result = re.match(target, f)
            if result:
                self.my_list.append(str(f))

    def close(self):
        ''' nothing '''
        pass

    def write(self, text):
        ''' nothing '''
        pass

    def read(self, length: int):
        ''' nothing '''
        pass

    def readline(self) -> str:
        ans = b''
        if 0 < len(self.my_list):
            ans = self.my_list[0]
            self.my_list = self.my_list[1:]
            # print(f"MyFindfirst {str(self.my_list)}")
            ans = ans.encode('utf-8')
        else:
            raise OSError('readline exception')
        return ans


class MyAbstract(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def send_ready(self) -> bool:
        pass

    @abstractmethod
    def send(self, message):
        pass

    @abstractmethod
    def recv_ready(self) -> bool:
        pass

    @abstractmethod
    def recv(self, length: int):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def is_active(self) -> int:
        pass

    @abstractmethod
    def get_echo(self) -> bool:
        return True


class MyShell(MyAbstract):
    def __init__(self, command=None):
        if command is None:
            command = ['cmd']
        # print("MyShell __init__ start")
        self.data = ''
        self.lock = threading.Lock()
        self.active = 1
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
        )
        thread = MyShellThread(self, 'stdout', self.process.stdout)
        thread.start()
        # print('MyShell __init__ end')

    def get_lock(self) -> threading.Lock:
        return self.lock

    @typing.override
    def send_ready(self) -> bool:
        # print('send_ready')
        if self.active == 0:
            return 0
        return self.process.stdin.writable()

    @typing.override
    def send(self, message):
        # print(f"send /{message.strip()}/")
        if self.active == 0:
            return
        self.process.stdin.write(message)
        self.process.stdin.flush()

    @typing.override
    def recv_ready(self) -> bool:
        if 0 < len(self.data):
            return True  # 残りデータがあるなら無条件OK
        if self.active == 0:
            return False
        self.process.stdout.flush()
        return False

    @typing.override
    def recv(self, length: int):
        # print(f"recv d=/{self.data.strip()}/")
        if len(self.data) <= 0:
            return b''
        local_data = ''
        pos = length
        with self.get_lock():
            if 0 < pos:
                local_data = local_data + self.data[0]
                self.data = self.data[1:]
                pos = pos - 1
        return local_data.encode('utf-8')

    @typing.override
    def close(self):
        # print('client close')
        self.active = 0
        self.data = ''
        local_process = self.process
        self.local_process = None
        if local_process is not None:
            try:
                local_process.terminate()
            except Exception:
                # anything delete
                pass

    @typing.override
    def is_active(self) -> int:
        return self.active

    @typing.override
    def get_echo(self) -> bool:
        return True


class MyPexpect(MyAbstract):
    def __init__(self):
        shell_name = os.getenv('SHELL', '/bin/sh')
        self.child = pexpect.spawn(shell_name, timeout=0, encoding='utf-8')
        self.result = ''

    @typing.override
    def send_ready(self) -> bool:
        return True

    @typing.override
    def send(self, message):
        child = self.child
        if child is None:
            return
        child.send(message)

    @typing.override
    def recv_ready(self) -> bool:
        if self.result != '':
            return True  # 残りデータがあるなら無条件OK
        child = self.child
        if child is None:
            return False
        self.result = ''
        target = ''
        while True:
            index = child.expect([r'.', pexpect.EOF, pexpect.TIMEOUT])
            if index == 2:
                break  # timeout
            elif index == 1:
                self.close()
                break  # EOF
            #
            # child.after でマッチした文字列全体を取得
            target = child.before + child.after
            if len(target) <= 0:
                break  # 収集できなかった
            #
            # 文字列を加算
            self.result = self.result + target
        #
        return 0 < len(target)

    @typing.override
    def recv(self, length: int):
        if self.result == '' and not self.recv_ready():
            return ''
        if self.result == '':
            return ''
        if len(self.result) <= length:
            work = self.result
            self.result = ''
        else:
            work = self.result[:length]
            self.result = self.result[length + 1:]
        work = work.replace("\r", '')
        return work.encode('utf-8')

    @typing.override
    def close(self):
        child = self.child.close()
        self.child = None
        try:
            child.close()
        except Exception:
            pass

    @typing.override
    def is_active(self) -> int:
        if self.child is not None:
            return 1
        return 0

    @typing.override
    def get_echo(self) -> bool:
        return True


class MySerial(MyAbstract):
    def __init__(self, command: str, rate: int, flowctrl=3, flowctrl_dtr=False, flowctrl_rts=False):
        self.read_ser = None
        if platform.system().lower() != 'linux':
            # for Windows
            if 0 < len(command) and '0' <= command[0] and command[0] <= '9':
                # 1文字以上で 0-9の間ならCOMを追加する
                command = 'COM' + command
        if flowctrl is None:
            self.read_ser = serial.Serial(command, rate, timeout=0.1)
        else:
            xonxoff = flowctrl == 1  # default False
            rtscts = flowctrl == 2 or (flowctrl == 3 and flowctrl_rts)  # default False
            dsrdtr = flowctrl == 4 or (flowctrl == 3 and flowctrl_dtr)  # default False
            self.read_ser = serial.Serial(command, rate, timeout=0.1, xonxoff=xonxoff, rtscts=rtscts, dsrdtr=dsrdtr)
        self.data = b''

    @typing.override
    def send_ready(self) -> bool:
        if self.read_ser is None:
            return False
        return self.read_ser.writable()

    @typing.override
    def send(self, message):
        if self.read_ser is None:
            return
        self.read_ser.write(message.encode('utf-8'))

    @typing.override
    def recv_ready(self) -> bool:
        # print(f"recv_ready {self.data}/{len(self.data)}/{self.read_ser is None}")
        if 0 < len(self.data):
            return True  # 残りデータがあるなら無条件OK
        if self.read_ser is None:
            return False
        self.read_ser.flush()
        if not self.read_ser.readable():
            return False
        try:
            self.data = self.read_ser.read(size=256)
        except Exception:
            self.close()  # エラー がでたので強制終了
            return False
        return 0 < len(self.data)

    @typing.override
    def recv(self, length: int):
        self.recv_ready()
        if len(self.data) < length:
            result = self.data
            self.data = b''
            return result
        result = self.data[0:length]
        self.data = self.data[length:]
        return result

    @typing.override
    def close(self):
        try:
            localReadSer = self.read_ser
            self.read_ser = None
            if localReadSer is not None:
                localReadSer.close()
        except Exception:
            pass

    @typing.override
    def is_active(self) -> int:
        if self.read_ser is None:
            return 0
        return 1

    @typing.override
    def get_echo(self) -> bool:
        return True

    def exit_status_ready(self):
        return not self.is_active() != 0

    def getmodemstatus(self) -> int:
        result = 0
        if self.read_ser is None:
            return result
        try:
            if self.read_ser.cts():
                result = result + 1
        except OSError:
            pass
        try:
            if self.read_ser.dsr():
                result = result + 2
        except OSError:
            pass
        try:
            if self.read_ser.ri():
                result = result + 4
        except OSError:
            pass
        try:
            if self.read_ser.cd():
                result = result + 8
        except OSError:
            pass
        return result


class MyTelnetT0(MyAbstract):

    def __init__(self, client: socket.socket):
        self.client = client
        self.data = b''

    @typing.override
    def send_ready(self) -> bool:
        if self.client is None:
            return False
        return True

    @typing.override
    def send(self, message: str):
        if self.client is None:
            return
        self.send_binary(message.encode('utf-8'))

    def send_binary(self, message):
        if self.client is None:
            return
        self.client.sendall(message)

    @typing.override
    def recv_ready(self) -> bool:
        if 0 < len(self.data):
            return True  # 残りデータがあるなら無条件OK
        if self.client is None:
            return False
        try:
            self.client.settimeout(0.1)
            recv_data = self.client.recv(1024)
            if recv_data is None or recv_data == b'':
                self.close()
                return False
            self.data = self.change_stream(recv_data)
        except ConnectionResetError:
            self.close()
            return False
        except socket.timeout:
            return False
        return 0 < len(self.data)

    @typing.override
    def change_stream(self, recv_data):
        return recv_data

    @typing.override
    def recv(self, length: int):
        if 0 == len(self.data):  # 残りデータがない
            if self.client is None:  # closeである
                return None
        self.recv_ready()
        if len(self.data) < length:
            result = self.data
            self.data = b''
            return result
        result = self.data[0:length]
        self.data = self.data[length:]
        return result

    @typing.override
    def close(self):
        local_client = self.client
        self.client = None
        if local_client is not None:
            try:
                local_client.close()
            except Exception:
                pass

    @typing.override
    def is_active(self) -> int:
        if self.client is not None:
            return 1
        return 0

    @typing.override
    def get_echo(self) -> bool:
        return True

    def exit_status_ready(self):
        return self.client is None


class MyTelnetT1(MyTelnetT0):

    _CR = b'\r'
    _LF = b'\n'

    _NULL = b'\x00'                 # 0 Binary Transmission [RFC856]
    _ECHO = b'\x01'                 # 1 Echo [RFC857]
    _Reconnection = b'\x02'         # 2 Reconnection [NIC 15391 of 1973]
    _Suppress_Go_Ahead = b'\x03'    # 3 Suppress Go Ahead [RFC858]
    _AMSize_Negotiation = b'\x04'   # 4 Approx Message Size Negotiation [NIC 15393 of 1973]
    _Status = b'\x05'               # 5 Status [RFC859]
    _Timing_Mark = b'\x06'          # 6 Timing Mark [RFC860]
    _RCTrans_and_Echo = b'\x07'     # 7 Remote Controlled Trans and Echo [RFC726]
    _Output_Line_Width = b'\x08'    # 8 Output Line Width [NIC 20196 of August 1978]
    _Output_Page_Size = b'\x09'     # 9 Output Page Size [NIC 20197 of August 1978]
    _OCRDisposition = b'\x0a'       # 10 Output Carriage-Return Disposition [RFC652]
    _OHTStops = b'\x0b'             # 11 Output Horizontal Tab Stops [RFC653]
    _OHTDisposition = b'\x0c'       # 12 Output Horizontal Tab Disposition [RFC654]
    _OFDisposition = b'\x0d'        # 13 Output Formfeed Disposition [RFC655]
    _OVTabstops = b'\x0e'           # 14 Output Vertical Tabstops [RFC656]
    _OVTab_Disposition = b'\x0f'    # 15 Output Vertical Tab Disposition [RFC657]
    _OLDisposition = b'\x10'        # 16 Output Linefeed Disposition [RFC658]
    _Extended_ASCII = b'\x11'       # 17 Extended ASCII [RFC698]
    _Logout = b'\x12'               # 18 Logout [RFC727]
    _Byte_Macro = b'\x13'           # 19 Byte Macro [RFC735]
    _Data_Entry_Terminal = b'\x14'  # 20 Data Entry Terminal [RFC1043][RFC732]
    _SUPDUP = b'\x15'               # 21 SUPDUP [RFC736][RFC734]
    _SUPDUP_Output = b'\x16'        # 22 SUPDUP Output [RFC749]
    _Send_Location = b'\x17'        # 23 Send Location [RFC779]
    _Terminal_Type = b'\x18'        # 24 Terminal Type [RFC1091]
    _End_of_Record = b'\x19'        # 25 End of Record [RFC885]
    _TACACS_UI = b'\x1a'            # 26 TACACS User Identification [RFC927]
    _Output_Marking = b'\x1b'       # 27 Output Marking [RFC933]
    _TLocation_Number = b'\x1c'     # 28 Terminal Location Number [RFC946]
    _Telnet_3270_Regime = b'\x1d'   # 29 Telnet 3270 Regime [RFC1041]
    _X_3_PAD = b'\x1e'              # 30 X.3 PAD [RFC1053]
    _NAWS = b'\x1f'                 # 31 Negotiate About Window Size [RFC1073]
    _Terminal_Speed = b'\x20'       # 32 Terminal Speed [RFC1079]
    _RFC = b'\x21'                  # 33 Remote Flow Control [RFC1372]
    _Linemode = b'\x22'             # 34 Linemode [RFC1184]
    _X_Display_Location = b'\x23'   # 35 X Display Location [RFC1096]
    _EnvironmentOpt = b'\x24'       # 36 Environment Option [RFC1408]
    _Authentication_Opt = b'\25'    # 37 Authentication Option [RFC2941]
    _EncryptionOpt = b'\x26'        # 38 Encryption Option [RFC2946]
    _New_EnvironmentOpt = b'\x27'   # 39 New Environment Option [RFC1572]

    _EOF = b'\xF6'   # 236 [RFC1184]
    _SE = b'\xF0'    # 240 [RFC854][RFC855]
    _SB = b'\xFA'    # 250 [RFC854][RFC855]
    _WILL = b'\xFB'  # 251 [RFC854][RFC855]
    _WONT = b'\xFC'  # 252 [RFC854][RFC855]
    _DO = b'\xFD'    # 253 [RFC854][RFC855]
    _DONT = b'\xFe'  # 254 [RFC854][RFC855]
    _IAC = b'\xff'   # 255 [RFC854][RFC855]

    _IS = b'\x00'     # [RFC2941]
    _SEND = b'\x01'   # [RFC2941]
    _REPLY = b'\x02'  # [RFC2941]
    _NAME = b'\x03'   # [RFC2941]

    def __init__(self, client: socket.socket):
        super().__init__(client)
        self.recv_data = b''
        self.state = MyTelnetT1._NULL  # text
        self.sb_se_op = b''
        self.sb_se = b''
        self.alread_flag = {}
        self.init_sender()

    def init_sender(self):
        ''' echo '''
        self.send_binary(MyTelnetT1._IAC + MyTelnetT1._DO + MyTelnetT1._ECHO)

    def is_alread_flag(self, bynary_data, do_or_will) -> bool:
        key = bynary_data
        if do_or_will:
            key = key + b'd'
        else:
            key = key + b'w'
        flag = False
        if key in self.alread_flag:
            flag = True
        else:
            self.alread_flag[key] = True
        return flag

    def print(self, text):
        ''' for debug '''
        # print(text)
        pass

    @typing.override
    def change_stream(self, recv_data):
        self.recv_data = self.recv_data + recv_data
        mess = b''
        # print(f"change_stream start {self.recv_data}")
        while 0 < len(self.recv_data):
            # print(f"xx {mess} / {self.recv_data} / {len(self.recv_data)} /s={self.state} / {MyTelnetT1._NULL}")
            char_data = self.recv_data[0:1]
            self.recv_data = self.recv_data[1:]
            if self.state == MyTelnetT1._NULL:
                if char_data == MyTelnetT1._IAC:
                    self.state = char_data
                elif char_data == MyTelnetT1._CR:
                    self.state = char_data
                elif char_data == MyTelnetT1._EOF:
                    pass
                else:
                    mess = mess + char_data
            elif self.state == MyTelnetT1._IAC:
                if char_data == MyTelnetT1._IAC:
                    # IACを送りたい場合のエスケープ情報。
                    # だが送ると UTF-8 が壊れるので送らない
                    self.state = MyTelnetT1._NULL
                elif char_data == MyTelnetT1._WILL:
                    self.state = char_data
                elif char_data == MyTelnetT1._WONT:
                    self.state = char_data
                elif char_data == MyTelnetT1._DO:
                    self.state = char_data
                elif char_data == MyTelnetT1._DONT:
                    self.state = char_data
                elif char_data == MyTelnetT1._SB:
                    self.state = MyTelnetT1._SB + b'op'
                else:
                    self.state = MyTelnetT1._NULL
                    mess = mess + b'IAC_Unkown'
            elif self.state == MyTelnetT1._WILL:
                self.print(f"IAC WILL {char_data[0]}")
                self.state = MyTelnetT1._NULL
                if self.is_alread_flag(char_data, True):
                    pass  # 一度受信したことがあるものは２度と応答しない
                elif char_data == MyTelnetT1._ECHO:
                    self.do_iac_will_echo(char_data)
                else:
                    self.do_iac_will_any(char_data)
                    # 上記以外は _WONT を返す
                    self.send_binary(MyTelnetT1._IAC + MyTelnetT1._DONT + char_data)
                    self.print(f"res IAC DONT {char_data[0]}")
            elif self.state == MyTelnetT1._WONT:
                self.print(f"IAC WONT {char_data[0]}")
                self.state = MyTelnetT1._NULL
                if self.is_alread_flag(char_data, True):
                    pass  # 一度受信したことがあるものは２度と応答しない
                else:
                    self.do_iac_do_any(char_data)  # WONTに対してはWONTしか返せない
            elif self.state == MyTelnetT1._DO:
                self.print(f"IAC DO {char_data[0]}")
                self.state = MyTelnetT1._NULL
                if self.is_alread_flag(char_data, False):
                    pass  # 一度受信したことがあるものは２度と応答しない
                elif char_data == MyTelnetT1._ECHO:
                    self.do_iac_do_echo(char_data)
                elif char_data == MyTelnetT1._NAWS:
                    self.do_iac_do_NAWS(char_data)
                elif char_data == MyTelnetT1._Terminal_Type:
                    self.do_iac_do_Terminal_Type(char_data)
                else:
                    self.do_iac_do_any(char_data)  # 上記以外は _WONT を返す
            elif self.state == MyTelnetT1._DONT:
                self.print(f"IAC DONT {char_data[0]}")
                self.state = MyTelnetT1._NULL
                if self.is_alread_flag(char_data, False):
                    pass  # 一度受信したことがあるものは２度と応答しない
                else:
                    self.do_iac_will_any(char_data)  # WONTに対してはWONTしか返せない
            elif self.state == MyTelnetT1._SB + b'op':
                # IAC SB option の option受付
                self.sb_se = b''
                self.sb_se_op = char_data
                self.state = MyTelnetT1._SB
                self.print(f"IAC1 SB {self.sb_se_op} / {char_data}")
            elif self.state == MyTelnetT1._SB:
                # IAC SB option 後のデータ受付
                if char_data == MyTelnetT1._IAC:
                    # IAC SB option 後のデータ内に IAC を見つけた
                    self.state = MyTelnetT1._IAC + MyTelnetT1._SB
                else:
                    self.sb_se = self.sb_se + char_data
                self.print(f"IAC2 SB {self.sb_se_op} {self.sb_se} {self.sb_se_op}")
            elif self.state == MyTelnetT1._IAC + MyTelnetT1._SB:
                self.print(f"IAC SB {self.sb_se_op} IAC")
                # IAC SB option 後のデータ内に IAC を見つけた次の文字
                if char_data == MyTelnetT1._SE:
                    # IAC SB ... IAC SE まで完了した
                    self.state = MyTelnetT1._NULL
                    self.do_iac_sb_se()
                else:
                    # IACの後続が SBでなかったので データ受付継続
                    # self.print(f"IAC SB {self.sb_se_op} IAC {char_data[0]}")
                    self.state = MyTelnetT1._SB
                    self.sb_se = self.sb_se + MyTelnetT1._IAC + char_data
            elif self.state == MyTelnetT1._CR:
                self.state = MyTelnetT1._NULL
                if char_data == MyTelnetT1._CR:
                    mess = mess + MyTelnetT1._CR  # CR のエスケープです
                elif char_data == MyTelnetT1._NULL:  # teraterm だとこれ
                    mess = mess + MyTelnetT1._CR
                elif char_data == MyTelnetT1._LF:  # windowsのtelnetだとこれ
                    mess = mess + MyTelnetT1._CR
                else:
                    mess = mess + char_data  # CR を除いたものを入れます
            else:
                raise TypeError(f"Stateus error {int(self.state)}/{char_data[0]}")
        # print(f"change_stream end /{mess}/")
        return mess

    def do_iac_will_echo(self, char_data):
        ''' サーバが echo になることは受け入れる '''
        self.send_binary(MyTelnetT1._IAC + MyTelnetT1._DO + char_data)
        self.print(f"res IAC DONT {char_data[0]}")

    def do_iac_do_echo(self, char_data):
        ''' クライアントが echo にはなりたくない '''
        self.do_iac_do_any(char_data)

    def do_iac_will_any(self, char_data):
        ''' 基本 DONT を返す '''
        self.send_binary(MyTelnetT1._IAC + MyTelnetT1._DONT + char_data)
        self.print(f"res IAC DONT {char_data[0]}")

    def do_iac_do_any(self, char_data):
        ''' 基本 WONT を返す '''
        self.send_binary(MyTelnetT1._IAC + MyTelnetT1._WONT + char_data)
        self.print(f"res IAC WONT {char_data[0]}")

    def do_iac_do_NAWS(self, char_data):
        self.send_binary(MyTelnetT1._IAC + MyTelnetT1._WILL + char_data
                         + MyTelnetT1._IAC + MyTelnetT1._SB + char_data
                         + b'\0' + b'\x50' + b'\0' + b'\x18'
                         + MyTelnetT1._IAC + MyTelnetT1._SE)
        self.print("res IAC WILL NAWS IAC SB NAWS 80x24 IAC SE")

    def do_iac_do_Terminal_Type(self, char_data):
        self.send_binary(MyTelnetT1._IAC + MyTelnetT1._WILL + char_data
                         + MyTelnetT1._IAC + MyTelnetT1._SB + char_data
                         + MyTelnetT1._IS + b'VT100'
                         + MyTelnetT1._IAC + MyTelnetT1._SE)

    def do_iac_sb_se(self):
        self.print(f"IAC SB {self.sb_se_op} / {self.sb_se} IAC SE")
        # TODO:


class MyShellThread(threading.Thread):
    def __init__(self, myShell: MyShell, name: str, stream):
        # print("MyShellThread __init__ start")
        super().__init__()
        self.name = name
        self.myShell = myShell
        self.stream = stream
        # print("MyShellThread __init__ end")

    def run(self):
        ''' Thread starter '''
        # print(f"MyShellThread_run() start f={type(self.myShell)} n={self.name}")
        while self.myShell.is_active() != 0:
            ans = self.stream.read(1)
            # print(f"start n={self.name} a=/{ans}/")
            with self.myShell.get_lock():
                self.myShell.data = self.myShell.data + ans
        # print(f"MyShellThread_run() end n={self.name} a=/{ans}/")
        #
        # activeでなくなったので念のため消す
        try:
            self.stream.close()
        except Exception:
            # どんなエラーがでようと必ず殺す
            pass


class Label:
    ''' For Label '''

    def __init__(self, token_list):
        ''' __init__ '''
        self.token_list = token_list

    def getTokenList(self):
        ''' get token list '''
        return self.token_list

    def __str__(self):
        return f"{str(self.token_list)}"


class TtlContinueFlagException(Exception):
    ''' For continue '''

    def __init__(self, message):
        ''' __init__ '''
        super().__init__(message)


class TtlBreakFlagException(Exception):
    ''' For break '''

    def __init__(self, message):
        ''' __init__ '''
        super().__init__(message)


class TtlReturnFlagException(Exception):
    ''' For return '''

    def __init__(self, message):
        ''' __init__ '''
        super().__init__(message)


class TtlExitFlagException(Exception):
    ''' For exit'''

    def __init__(self, message):
        ''' __init__ '''
        super().__init__(message)


class TtlResultFlagException(Exception):
    ''' For return '''

    def __init__(self, message):
        ''' __init__ '''
        super().__init__(message)


class TtlGotoFlagException(Exception):
    ''' For Goto '''

    def __init__(self, message, line, label):
        ''' __init__ '''
        super().__init__(message)
        self.line = line
        self.label = label


class TtlParseTreeVisitor(ParseTreeVisitor):
    def visit(self, tree):
        return tree.accept(self)

    def visitChildren(self, node):
        result = {}
        result['name'] = node.__class__.__name__
        line_number = node.start.line
        result['line'] = line_number
        #
        n = node.getChildCount()
        if n == 0:
            return result
        worker_list = []
        for i in range(n):
            c = node.getChild(i)
            childResult = c.accept(self)
            if childResult is not None:
                worker_list.append(childResult)
        if worker_list != 0:
            result['child'] = worker_list
        return result

    def visitTerminal(self, node):
        type = node.getSymbol().type
        # print(f"visitErrorNode type={type} text={node.getText()}")
        if type < 0:
            return None
        x = TtlParserLexer.ruleNames[type - 1]
        if x == 'RN' or x == 'WS':
            return None
        return node.getText()

    def visitErrorNode(self, node):
        x = node.getSymbol().type
        x = TtlParserLexer.ruleNames[x - 1]
        y = node.getText()
        line_number = node.getSymbol().line
        raise TypeError(f"### l={str(line_number)} visitErrorNode type={x} text={y}")


class ThrowingErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise TypeError(f"### l={line}:{column} Token recognition error - {msg}")


class SplitEscape():

    split_escape_buffer = ''
    split_escape_state = 0

    def split_escape(self, text: str) -> str:
        '''
        装置から収集されたテキストがエスケープにより色付けされていると
        なにかと困るので ここで取る。
        ただし、本来であれば以下でエスケープはとれるのだが、
        行間またぐと取れないので独自実装を入れた
        ansi_escape = re.compile('\x1B\\[\\d+([;\\d]+){0,2}m')
        return ansi_escape.sub('', text)
        '''
        result = ''
        for char in text:
            if self.split_escape_state == 0:
                if char == "\x1b":
                    self.split_escape_state = 1
                    self.split_escape_buffer = char
                else:
                    result = result + char
            elif self.split_escape_state == 1:
                self.split_escape_buffer = self.split_escape_buffer + char
                if char == '[':
                    self.split_escape_state = 2
                else:
                    result = result + self.split_escape_buffer
                    self.split_escape_state == 0
                    self.split_escape_buffer = ''
            else:
                self.split_escape_buffer = self.split_escape_buffer + char
                if '0' <= char and char <= '9':
                    pass
                elif char == ';':
                    self.split_escape_state = self.split_escape_state + 1
                    if 5 <= self.split_escape_state:
                        result = result + self.split_escape_buffer
                        self.split_escape_state = 0
                        self.split_escape_buffer = ''
                elif char == 'm':
                    self.split_escape_state = 0
                    self.split_escape_buffer = ''
                else:
                    result = result + self.split_escape_buffer
                    self.split_escape_state = 0
                    self.split_escape_buffer = ''
        return result


class TtlPaserWolker(ABC, SplitEscape):
    ''' worker '''

    def __init__(self):
        ''' init '''
        if IMP_ERR:
            raise ImportError(IMP_ERR)
        self.value_list = {}
        self.result_file_json = {}
        self.end_flag = False
        self.client = None
        self.shell = None
        self.stdout = ''
        self.file_handle_list = {}
        self.title = 'dummy'
        self.title = self.get_title()  # オーバーライドされたときにタイトルを差し替える
        self.log_file_handle = None
        self.log_start = True
        self.log_timestamp_type = -1
        self.log_login_time = time.time()
        self.log_connect_time = None
        # カレントフォルダを取得する
        self.current_dir = pathlib.Path.cwd()
        #
        self.encrypt_file = {}
        self.exitcode = None
        #
        self.speed = 9600
        self.flowctrl = 3
        self.flowctrl_rts = False
        self.flowctrl_dtr = False

    def stop(self, error=None):
        ''' forced stop '''
        #
        self.end_flag = True
        #
        if error is not None:
            self.set_value('error', error)
            self.set_value('result', 0)
        #
        # SSH接続していたら止める
        self.close_client()
        #
        # ファイルハンドルがいたら止める
        for k in list(self.file_handle_list.keys()):
            self.do_fileclose(k)
        #
        # ログファイルハンドルがいたら止める
        self.do_logclose()
        #
        # カレントフォルダを戻す
        os.chdir(self.current_dir)

    def close_client(self):
        '''close client'''
        # print("close_client()")
        self.stdout = ''
        self.log_connect_time = None
        #
        client = self.client
        self.client = None
        if client is not None:
            try:
                client.close()
            except Exception:
                # どんなエラーがでようと必ず殺す
                client = self.client
        #
        shell = self.shell
        self.shell = None
        if shell is not None:
            try:
                shell.close()
            except Exception:
                # どんなエラーがでようと必ず殺す
                pass

    def set_default_value(self, param_list: list):
        #
        self.set_value('error', '')
        self.set_value('result', 1)
        #
        # print(f" data={json.dumps(param_list, indent=2)}")
        for i in range(10):
            self.set_value('param' + str(i + 1), '')
            self.set_value('param[' + str(i + 1) + ']', '')
        #
        for i, param in enumerate(param_list):
            self.set_value('param' + str(i + 1), param)
            self.set_value('param[' + str(i + 1) + ']', param)

    def execute(self, filename: str, param_list: list, data=None, ignore_result=False, goto_label=None):
        try:
            if goto_label is not None:
                self.do_goto_context(goto_label.line, goto_label.label)
            else:
                self.set_default_value(param_list)
                #
                # 一発目のinclude
                self.include(filename, data)
                #
                if self.exitcode is not None:
                    self.set_value('result', self.exitcode)
                if not ignore_result:
                    result = int(self.get_value('result'))
                    error_data = self.get_value('error')
                    if result == 0:
                        raise TtlResultFlagException(f"Exceptiont (result==0) f={filename} e=/{error_data}/")
            #
        except TtlGotoFlagException as goto_label:
            tb_obj = goto_label.__traceback__
            target_list = [
                'self.do_for_next_context(',
                'self.do_while_endwhile_context(',
                'self.do_until_enduntil_context(',
                'self.do_loopContext(']
            for x in traceback.format_tb(tb_obj):
                for target in target_list:
                    if target in x:
                        raise TypeError(f"## l={goto_label.line} Please use break or continue!")
            self.execute(filename, param_list, data, ignore_result, goto_label)
        finally:
            # なにがあろうとセッションは必ず殺す
            self.close_client()

    def include(self, filename: str, data=None):
        if self.end_flag:
            return
        #
        # 読み込みここから
        self.include_only(filename, data)
        #
        if self.end_flag:
            return
        #
        # 実処理ここから
        try:
            #
            self.do_statement_context(self.result_file_json[filename]['child'])
            #
        except TtlGotoFlagException:
            raise  # メッセージも出さずそのまま上流へ送る
        except TtlExitFlagException:
            # exit, goto コマンドが呼び出されときは正常終了です
            pass
        except Exception as e:
            self.set_log_inner(f"### except include f={str(e)}")
            self.stop(f"{type(e).__name__} f={filename} e={str(e)} error!")
            raise  # そのまま上流へ送る

    def include_only(self, filename: str, data=None):
        ''' include only '''
        try:
            #
            # print(f"filename={filename} param={self.result_file_json}")
            if filename not in self.result_file_json:
                if data is None:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = f.read()
                result_json = self.include_data(data)
                #
                # for call command
                self.result_file_json[filename] = result_json
                #
                # ラベル設定
                self.correct_label()
                #
        except Exception as e:
            self.set_log_inner(f"### except read file exception! f={str(e)}")
            self.stop(f"{type(e).__name__} f={filename} e={str(e)} error!")
            raise  # そのまま上流へ送る

    def include_data(self, data: str):
        ''' get Json from data '''
        if self.end_flag:
            return
        #
        input_stream = InputStream(data + "\n")
        lexer = TtlParserLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(ThrowingErrorListener())
        token_stream = CommonTokenStream(lexer)
        parser = TtlParserParser(token_stream)
        #
        # パーサが失敗していたら止める
        # parser._errHandler = BailErrorStrategy()
        #
        tree = parser.statement()
        visitor = TtlParseTreeVisitor()
        return tree.accept(visitor)

    def normpath(self, filename: str) -> str:
        filename = os.path.normpath(filename.replace("\\", '/'))
        if platform.system().lower() == 'linux':
            result = re.search('^([a-zA-Z]):(.*)$', filename)
            if result:
                filename = f"/mnt/{result.group(1)}/{result.group(2)}"
        return filename

    def set_value(self, strvar: str, data):
        ''' set ttl value '''
        # print(f"setValue={strvar} data={data}")
        if strvar in self.value_list:  # this is label
            if isinstance(self.get_value(strvar), Label):
                raise TypeError(f"Label already set exception. v={strvar}")
        self.value_list[strvar] = data

    def set_value_label(self, strvar: str, data: Label):
        ''' set ttl value for label '''
        # print(f"01ラベルを設定した {strvar} /{data.getTokenList()}/")
        self.value_list[strvar] = data

    def get_value(self, strvar: str, error_stop=True):
        ''' set ttl value '''
        if strvar not in self.value_list:
            for k in self.value_list:
                # print(k)
                if strvar + '[' in k:
                    return 'ARRAY'  # 配列指定がある
            if error_stop:
                raise TypeError(f"Value not found err v={strvar}")
            return None
        # print(f"02ラベルを取得した {strvar} // {self.value_list[strvar]}")
        return self.value_list[strvar]

    def get_data_int(self, data) -> int:
        try:
            result = self.get_data(data)
            result = int(result)
        except (TypeError, ValueError) as e:
            if isinstance(data, dict):
                if 'line' in data:
                    raise TypeError(f"### l={data['line']} {type(e).__name__} e={e}")
            raise  # そのまま上流へ送る
        return result

    def get_data_str(self, data) -> str:
        return str(self.get_data(data))

    def get_data(self, data):
        ''' get value from data '''
        result = ''
        try:
            if isinstance(data, str):
                result = self.get_value(data)
            elif 'name' not in data:
                raise TypeError(f"unkown name data={str(data)}")
            elif 'P11ExpressionContext' == data['name']:
                result = self.do_p11_expression(data['child'])
            elif 'P10ExpressionContext' == data['name']:
                result = self.do_p10_expression(data['child'])
            elif 'P9ExpressionContext' == data['name']:
                result = self.do_p9_expression(data['child'])
            elif 'P8ExpressionContext' == data['name']:
                result = self.do_p8_expression(data['child'])
            elif 'P7ExpressionContext' == data['name']:
                result = self.do_p7_expression(data['child'])
            elif 'P6ExpressionContext' == data['name']:
                result = self.do_p6_expression(data['child'])
            elif 'P5ExpressionContext' == data['name']:
                result = self.do_p5_expression(data['child'])
            elif 'P4ExpressionContext' == data['name']:
                result = self.do_p4_expression(data['child'])
            elif 'P3ExpressionContext' == data['name']:
                result = self.do_p3_expression(data['child'])
            elif 'P2ExpressionContext' == data['name']:
                result = self.do_p2_expression(data['child'])
            elif 'P1ExpressionContext' == data['name']:
                result = self.do_p1_expression(data['child'])
            elif 'IntExpressionContext' == data['name']:
                result = self.do_int_expression_context(data['child'])
            elif 'StrExpressionContext' == data['name']:
                result = self.do_str_expression_context(data['child'])
            elif 'IntContextContext' == data['name']:
                result = self.int_context(data['child'])
            elif 'StrContextContext' == data['name']:
                result = self.do_str_context(data['child'])
            elif 'KeywordContext' == data['name']:
                result = self.get_keyword(data)
            else:
                raise TypeError(f"unkown keyword n={data['name']}")
        except ZeroDivisionError as e:
            if isinstance(data, dict):
                if 'line' in data:
                    raise TypeError(f"### l={data['line']} {type(e).__name__} e={e}")
            raise  # そのまま上流へ送る
        return result

    def get_keyword(self, data):
        ''' get value in keyword '''
        # print(f"get_keyword data={data}")
        return self.get_value(self.get_key_name(data))

    def get_key_name(self, data) -> str:
        ''' get keyword name from data '''
        # print(f"keywordName {data}")
        if 'name' not in data:
            if isinstance(data, str):
                return data
            elif isinstance(data, list):
                return data[0]
            raise TypeError("keywordName name not in data")
        #
        # this is dict
        if 'StrExpressionContext' == data['name']:
            return self.get_key_name(data['child'][0])
        elif 'KeywordContext' != data['name']:
            raise TypeError(
                f"### l={data['line']} keywordName name is not KeywordContext {data}"
            )
        #
        data = data['child']
        # print(f"data={data} len={len(data)}")
        if len(data) == 1:
            # 単純指定
            return data[0]
        else:
            # 配列対策
            index = data[2]
            index = self.get_data(index)
            return data[0] + '[' + str(int(index)) + ']'

    def set_log_inner(self, strvar: str):
        ''' get log for self class '''
        #
        strvar = strvar.replace("\r\n", "\n")
        strvar = strvar.replace("\r", "\n")
        if "\n" != os.linesep:
            strvar = strvar.replace("\n", os.linesep)
        # ログ出力/オーバーライドする方に渡す
        self.set_log(strvar)
        #
        # ログ出力処理
        if self.log_start:
            self.do_logwrite(strvar)

    @abstractmethod
    def set_log(self, strvar: str):
        ''' Please Override! '''
        pass

    def correct_label(self):
        ''' collect label '''
        self.correct_label_all(self.result_file_json.values())

    def correct_label_all(self, token_list_list: list):
        ''' collect all label '''
        i = -1
        for token_dict in token_list_list:
            i = i + 1
            name = token_dict['name']  # StatementContext
            # print(f"correctLabelAll i={i} {name}")
            if "StatementContext" == name:
                # print("hit")
                self.correct_label_all(token_dict['child'])  # StatementContext
            elif 'CommandlineContext' == name:
                # print("hit2")
                j = -1
                next_list = token_dict['child']
                for next in next_list:
                    j = j + 1
                    if 'LabelContext' == next['name']:
                        # print(f"hot3 {next['child']}")
                        label_name = next['child'][1]
                        # print("hit4")
                        label = Label(token_list_list[i + 1:])
                        # print(f"xxx data={label_name} // {label.getTokenList()}")
                        self.set_value_label(label_name, label)
            #
            if self.end_flag:
                break

    def print_command(self, name: str, line: int, data_list) -> str:
        message = f"### l={line} c={name}"
        for data in data_list:
            keywordName = None
            try:
                keywordName = self.get_key_name(data)
            except TypeError:
                # print(f"type error {e}")
                pass
            result = self.get_data(data)
            if isinstance(result, int):
                result = str(result)
            elif isinstance(result, Label):
                result = 'LABEL'
            if keywordName is None:
                message = message + f" p({result})"
            else:
                message = message + f" p({keywordName}/{result})"
        self.set_log_inner(message + "\n")
        return message

    def do_statement_context(self, x_list, ifFlag=1):
        '''execute_result'''
        # print("execute_result")
        if self.end_flag:
            return
        for x in x_list:
            name = x['name']
            line = x['line']
            #
            if 'CommandlineContext' == name:
                if ifFlag != 0:
                    self.do_commandline_context(x['child'])
            elif 'ElseifContext' == name:
                if ifFlag == 0:
                    first = self.get_data_int(x['child'][1])
                    if first != 0:
                        self.do_statement_context(x['child'][3:])
                        ifFlag = 1
            elif 'ElseContext' == name:
                if ifFlag == 0:
                    self.do_statement_context(x['child'][1:])
            else:
                self.stop(error=f"### l={line} execute_result Unkown name={name} x={x}")
            if self.end_flag:
                break

    def do_commandline_context(self, token_list):
        for x in token_list:
            # print(f"do_commandline_context data={json.dumps(x, indent=2)}")
            name = x['name']
            line = x['line']
            if self.end_flag:
                break
            elif 'InputContext' == name:
                strvar = self.get_key_name(x['child'][0])
                data = x['child'][2]
                data = self.get_data(data)
                self.set_value(strvar, data)
            elif 'CommandContext' == name:
                command_name = x['child'][0]
                if 'assert' == command_name:
                    self.do_assert(command_name, line, x['child'][1:])
                elif 'bplusrecv' == command_name:
                    self.do_bplusrecv(command_name, line)
                elif 'bplussend' == command_name:
                    p1 = self.get_data(x['child'][1])
                    self.do_bplussend(command_name, line, p1)
                elif 'callmenu' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_callmenu(command_name, line, p1)
                elif command_name in ['setdir', 'changedir']:
                    p1 = self.get_data(x['child'][1])
                    self.do_changedir(p1)
                elif 'clearscreen' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_clearscreen(command_name, line, p1)
                elif command_name in ['closett', 'disconnect', 'unlink']:
                    self.close_client()
                elif 'connect' == command_name:
                    self.do_connect(self.get_data(x['child'][1]), line)
                elif 'dispstr' == command_name:
                    self.do_dispstr(x['child'][1:])
                elif 'enablekeyb' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_enablekeyb(command_name, line, p1)
                elif 'flushrecv' == command_name:
                    self.do_flushrecv()
                elif 'getmodemstatus' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.do_getmodemstatus(p1)
                elif 'gethostname' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.do_gethostname(p1)
                elif 'gettitle' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p1_val = self.get_title()
                    self.set_value(p1, p1_val)
                elif 'logautoclosemode' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_logautoclosemode(command_name, line, p1)
                elif 'logclose' == command_name:
                    self.do_logclose()
                elif 'loginfo' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.do_loginfo(command_name, line, p1)
                elif 'logopen' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    p3 = self.get_data_int(x['child'][3])
                    p_len = len(x['child'])
                    p4 = 0
                    if 5 < p_len:
                        p4 = self.get_data_int(x['child'][4])
                    p5 = 0
                    if 6 <= p_len:
                        p5 = self.get_data_int(x['child'][5])
                    p6 = 0
                    if 7 <= p_len:
                        p6 = self.get_data_int(x['child'][6])
                    p7 = 0
                    if 8 <= p_len:
                        p7 = self.get_data_int(x['child'][7])
                    p8 = 0
                    if 9 <= p_len:
                        p8 = self.get_data_int(x['child'][8])
                    self.do_logopen(p1, p2, p3, p4, p5, p6, p7, p8)
                elif 'logpause' == command_name:
                    self.do_logpause()
                elif 'logrotate' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p_len = len(self.get_data(x['child']))
                    p2 = None
                    if 3 < p_len:
                        p2 = self.get_data_int(x['child'][2])
                    self.do_logrotate(command_name, line, p1, p2)
                elif 'logstart' == command_name:
                    self.do_logstart()
                elif 'logwrite' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_logwrite(p1)
                elif 'recvln' == command_name:
                    self.do_recvln()
                elif 'scprecv' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = p1
                    if 3 <= len(x['child']):
                        p2 = self.get_data_str(x['child'][2])
                    self.do_scprecv(p1, p2)
                elif 'scpsend' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = p1
                    if 3 <= len(x['child']):
                        p2 = self.get_data_str(x['child'][2])
                    self.do_scpsend(p1, p2)
                elif command_name in ['send', 'sendbinary', 'sendtext']:
                    self.do_send(x['child'][1:])
                elif 'sendbreak' == command_name:
                    self.do_sendbreak()
                elif 'sendln' == command_name:
                    self.do_sendln(x['child'][1:])
                elif ('setbaud' == command_name) or ('setspeed' == command_name):
                    p1 = self.get_data_int(x['child'][1])
                    self.do_setspeed(p1)
                elif 'setecho' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_setecho(line, p1)
                elif 'setflowctrl' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_setflowctrl(p1)
                elif 'setdtr' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_setdtr(p1)
                elif 'setrts' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_setrts(p1)
                elif 'settitle' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.set_title(p1)
                elif 'testlink' == command_name:
                    self.do_testlink()
                elif command_name in ['wait', 'wait4all']:
                    self.do_wait(x['child'][1:])
                elif 'waitln' == command_name:
                    self.do_waitln(x['child'][1:])
                elif 'break' == command_name:
                    raise TtlBreakFlagException(command_name)
                elif 'call' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.do_call(line, p1)
                elif 'continue' == command_name:
                    raise TtlContinueFlagException(command_name)
                elif 'end' == command_name:
                    self.stop()
                elif 'execcmnd' == command_name:
                    p1 = self.get_data(x['child'][1])
                    result_json = self.include_data(p1)
                    self.do_statement_context(result_json['child'])
                elif 'exit' == command_name:
                    raise TtlExitFlagException(command_name)
                elif 'goto' == command_name:
                    label = self.get_key_name(x['child'][1])
                    raise TtlGotoFlagException(command_name, line, label)
                elif 'include' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.include(p1)
                elif 'mpause' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_pause(p1 / 1000)
                elif 'pause' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_pause(p1)
                elif 'return' == command_name:
                    raise TtlReturnFlagException(command_name)
                elif 'code2str' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    self.do_code2str(p1, p2)
                elif 'expandenv' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = ''
                    if 3 <= len(x['child']):
                        p2 = self.get_data_str(x['child'][2])
                    else:
                        p2 = self.get_data_str(p1)
                    self.do_expandenv(p1, p2)
                elif 'int2str' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.set_value(p1, p2)
                elif 'sprintf' == command_name:
                    self.do_sprintf('inputstr', x['child'][1:])
                elif 'sprintf2' == command_name:
                    p1 = x['child'][1]
                    p1 = self.get_key_name(p1)
                    self.do_sprintf(p1, x['child'][2:])
                elif 'str2code' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_str2code(p1, p2)
                elif 'str2int' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    self.set_value(p1, p2)
                elif 'strcompare' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_strcompare(p1, p2)
                elif 'strconcat' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_strconcat(p1, p2)
                elif 'strcopy' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    p3 = self.get_data_int(x['child'][3])
                    p4 = self.get_key_name(x['child'][4])
                    self.do_strcopy(p1, p2, p3, p4)
                elif 'strinsert' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    p3 = self.get_data_str(x['child'][3])
                    self.do_strinsert(p1, p2, p3)
                elif 'strjoin' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = 9
                    if 4 <= len(x['child']):
                        p3 = self.get_data_int(x['child'][3])
                    self.do_strjoin(p1, p2, p3)
                elif 'strlen' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_strlen(p1)
                elif 'strmatch' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_strmatch(p1, p2)
                elif 'strremove' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    p3 = self.get_data_int(x['child'][3])
                    self.do_strremove(p1, p2, p3)
                elif 'strreplace' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    p3 = self.get_data_str(x['child'][3])
                    p4 = self.get_data_str(x['child'][4])
                    self.do_strreplace(p1, p2, p3, p4)
                elif 'strscan' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_strscan(p1, p2)
                elif 'strspecial' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = None
                    if 3 <= len(x['child']):
                        p2 = self.get_data_str(x['child'][2])
                    self.do_strspecial(p1, p2)
                elif 'strsplit' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = 10
                    if 4 <= len(x['child']):
                        p3 = self.get_data_int(x['child'][3])
                    self.do_strsplit(p1, p2, p3)
                elif 'strtrim' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_strtrim(p1, p2)
                elif 'tolower' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.set_value(p1, p2.lower())
                elif 'toupper' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.set_value(p1, p2.upper())
                elif 'basename' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p2 = self.normpath(p2)
                    p2 = os.path.basename(p2)
                    self.set_value(p1, str(p2))
                elif 'dirname' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_basename(p1, p2)
                elif command_name in ['fileclose', 'findclose']:
                    p1 = self.get_key_name(x['child'][1])
                    self.do_fileclose(p1)
                elif 'fileconcat' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_fileconcat(p1, p2)
                elif 'filecopy' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_filecopy(p1, p2)
                elif 'filecreate' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_fileopen(p1, p2, 0, 0)
                elif 'filedelete' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_filedelete(p1)
                elif 'fileopen' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = self.get_data_int(x['child'][3])
                    p4 = 0
                    if 5 <= len(x['child']):
                        p4 = self.get_data_int(x['child'][4])
                    self.do_fileopen(p1, p2, p3, p4)
                elif 'filereadln' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_key_name(x['child'][2])
                    self.do_filereadln(line, p1, p2)
                elif 'fileread' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    p3 = self.get_key_name(x['child'][3])
                    self.do_fileread(line, p1, p2, p3)
                elif 'filerename' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_filerename(p1, p2)
                elif 'filesearch' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_filesearch(p1)
                elif 'filestat' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_key_name(x['child'][2])
                    p3 = None
                    if 4 <= len(x['child']):
                        p3 = self.get_key_name(x['child'][3])
                    p4 = None
                    if 4 <= len(x['child']):
                        p4 = self.get_key_name(x['child'][4])
                    self.do_filestat(p1, p2, p3, p4)
                elif 'filetruncate' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    self.do_filetruncate(p1, p2)
                elif 'filewrite' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_filewrite(line, p1, p2)
                elif 'filewriteln' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    self.do_filewrite(line, p1, p2 + "\n")
                elif 'findfirst' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = self.get_key_name(x['child'][3])
                    self.do_findfirst(line, p1, p2, p3)
                elif 'findnext' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_key_name(x['child'][2])
                    self.do_findnext(line, p1, p2)
                elif 'foldercreate' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_foldercreate(p1)
                elif 'folderdelete' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_folderdelete(p1)
                elif 'foldersearch' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    self.do_foldersearch(p1)
                elif 'getdir' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.set_value(p1, str(pathlib.Path.cwd()))
                elif 'makepath' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = self.get_data_str(x['child'][3])
                    self.do_makepath(p1, p2, p3)
                elif command_name in ['setpassword', 'setpassword2']:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = self.get_data_str(x['child'][3])
                    p4 = 'anonymouse'
                    if 5 <= len(x['child']):
                        p4 = self.get_data_str(x['child'][4])
                    self.do_setpassword(p1, p2, p3, p4)
                elif command_name in ['getpassword', 'getpassword2']:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    p3 = self.get_key_name(x['child'][3])
                    p4 = 'anonymouse'
                    if 5 <= len(x['child']):
                        p4 = self.get_data_str(x['child'][4])
                    self.do_getpassword(p1, p2, p3, p4)
                elif command_name in ['ispassword', 'ispassword2']:
                    p1 = self.get_data(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_ispassword(p1, p2)
                elif command_name in ['delpassword', 'delpassword2']:
                    p1 = self.get_data(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_delpassword(p1, p2)
                elif 'checksum8' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_checksum8(p1, p2)
                elif 'checksum8file' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_checksum8file(p1, p2)
                elif 'checksum16' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_checksum16(p1, p2)
                elif 'checksum16file' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_checksum16file(p1, p2)
                elif 'checksum32' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_checksum32(p1, p2)
                elif 'checksum32file' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_checksum32file(p1, p2)
                elif 'crc16' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_crc16(p1, p2)
                elif 'crc16file' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_crc16file(p1, p2)
                elif 'crc32' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_crc32(p1, p2)
                elif 'crc32file' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data(x['child'][2])
                    self.do_crc32file(p1, p2)
                elif 'exec' == command_name:
                    self.do_exec(line, x['child'][1:])
                elif 'getdate' == command_name:
                    self.do_getdate(x['child'][1:])
                elif 'getenv' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_key_name(x['child'][2])
                    self.do_getenv(p1, p2)
                elif 'getipv4addr' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_key_name(x['child'][2])
                    self.do_getipv4addr(p1, p2)
                elif 'getipv6addr' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_key_name(x['child'][2])
                    self.do_getipv6addr(p1, p2)
                elif 'gettime' == command_name:
                    self.do_getdate(x['child'][1:], format='%H:%M:%S')
                elif 'getttdir' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.set_value(p1, self.current_dir)
                elif 'getver' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = None
                    if 3 <= len(x['child']):
                        p2 = float(self.get_data(x['child'][2]))
                    self.do_getver(p1, p2)
                elif 'ifdefined' == command_name:
                    p1 = str(x['child'][1])
                    self.do_ifdefined(p1)
                elif 'intdim' == command_name:
                    p1 = x['child'][1]
                    p2 = self.get_data_int(x['child'][2])
                    for i in range(p2):
                        self.set_value(p1 + '[' + str(i) + ']', 0)
                elif 'random' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    p2 = self.get_data_int(x['child'][2])
                    self.set_value(p1, random.randint(0, p2))
                elif 'setenv' == command_name:
                    p1 = self.get_data_str(x['child'][1])
                    p2 = self.get_data_str(x['child'][2])
                    os.environ[p1] = p2
                elif 'setexitcode' == command_name:
                    p1 = self.get_data_int(x['child'][1])
                    self.do_setexitcode(p1)
                elif 'strdim' == command_name:
                    p1 = x['child'][1]
                    p2 = self.get_data_int(x['child'][2])
                    for i in range(p2):
                        self.set_value(p1 + '[' + str(i) + ']', '')
                elif 'uptime' == command_name:
                    p1 = self.get_key_name(x['child'][1])
                    self.set_value(p1, int(uptime.uptime() * 1000))
                else:
                    self.do_command_context(command_name, line, x['child'][1:])
            elif 'ForNextContext' == name:
                self.do_for_next_context(x['child'])
            elif 'WhileEndwhileContext' == name:
                self.do_while_endwhile_context(x['child'])
            elif 'UntilEnduntilContext' == name:
                self.do_until_enduntil_context(x['child'])
            elif 'DoLoopContext' == name:
                self.do_loopContext(x['child'])
            elif 'If1Context' == name:
                self.do_if1_context(x['child'])
            elif 'If2Context' == name:
                self.do_if2_context(x['child'])
            elif 'LabelContext' == name:
                pass
            else:
                raise TypeError(f"### l={line} Unkown context name={name}")

    def do_command_context(self, name, line, data_list):
        ''' command context '''
        self.print_command(name, line, data_list)
        if 'passwordbox' == name or 'inputbox' == name:
            # GUIでしかできないのでダニーを入れておく
            # 必要なら do_command_context() を override してください
            # print(f"super.do_command_context {name} start")
            self.set_value('inputstr', 'aaa')
            # print(f"super.do_command_context {name} end")
        elif 'listbox' == name:
            # GUIでしかできないのでキャンセルにしておく
            # 必要なら do_command_context() を override してください
            self.set_value('result', -1)
        elif 'dirnamebox' == name:
            self.set_value('result', 1)
            self.set_value('inputstr', str(os.getcwd()))
        elif 'filenamebox' == name:
            self.set_value('result', 0)
            self.set_value('inputstr', 'tmp.txt')
        elif 'yesnobox' == name:
            self.set_value('result', 1)
        elif 'showtt' == name:
            self.set_value(self.get_key_name(data_list[0]), 0)
        elif name in [
            'bringupbox',
            'closesbox',
            'messagebox',
            'statusbox',
            'setdlgpos',
            'show'
        ]:
            pass
        else:
            self.print_command(name, line, data_list)
            raise TypeError(f"### l={line} Unsupport command={name}")

    def do_goto_context(self, line, label_str):
        #
        # print("gotoContest")
        label = self.get_value(label_str, error_stop=False)
        if label is None:
            raise TypeError(f"### l={line} No hit label error none label={label_str}")
        if not isinstance(label, Label):
            raise TypeError(f"### l={line} No hit label error label={label_str}")
        for token in label.getTokenList():
            self.do_statement_context([token])
            if self.end_flag:
                break

    def do_for_next_context(self, data_list):
        intvar = self.get_key_name(data_list[1])
        first = self.get_data_int(data_list[2])
        self.set_value(intvar, first)
        last = self.get_data_int(data_list[3])
        # print(f"for intvar={intvar} first={first} last={last}")
        add = -1
        if first < last:
            add = 1
        while True:
            #
            try:
                self.do_statement_context(data_list[4:-1])
                #
                if self.end_flag:
                    break
                #
                self.set_value(intvar, self.get_value(intvar) + add)
                if 0 < add:
                    if last < self.get_value(intvar):
                        break
                else:
                    if self.get_value(intvar) < last:
                        break
            except TtlContinueFlagException:
                pass
            except TtlBreakFlagException:
                break

    def do_while_endwhile_context(self, data_list):
        while self.get_data_int(data_list[1]) != 0:
            try:
                #
                self.do_statement_context(data_list[2:-1])
                #
                if self.end_flag:
                    break
            except TtlContinueFlagException:
                pass
            except TtlBreakFlagException:
                break

    def do_until_enduntil_context(self, data_list):
        while self.get_data_int(data_list[1]) == 0:
            try:
                #
                self.do_statement_context(data_list[2:-1])
                #
                if self.end_flag:
                    break
            except TtlContinueFlagException:
                pass
            except TtlBreakFlagException:
                break

    def do_loopContext(self, data_list):
        while True:
            try:
                for data in data_list:
                    if isinstance(data, str):
                        # do/loop
                        # print(f"do/loop={data}")
                        pass
                    elif 'CommandlineContext' == data['name']:
                        # print(f"LineContext={data}")
                        self.do_statement_context([data])
                    else:
                        # print(f"data={data['name']}")
                        value = self.get_data_int(data)
                        # print(f"value ={value}")
                        if value == 0:
                            # print(f"data ok={data}")
                            raise TtlBreakFlagException("do_loopContext")
            except TtlContinueFlagException:
                pass
            except TtlBreakFlagException:
                break

    def do_if1_context(self, data_list):
        first = self.get_data_int(data_list[1])
        # print(f"if1 first={first}")
        if 0 != first:
            self.do_statement_context(data_list[2:])

    def do_if2_context(self, data_list):
        first = self.get_data_int(data_list[1])
        # print(f"if2 first={first}")
        self.do_statement_context(data_list[3:-1], first)

    def do_p11_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        val2 = self.get_data_int(data[2])
        result = val1 or val2
        # print(f"p11 {val1:x}/{val2:x}/{result:x}")
        return result

    def do_p10_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        val2 = self.get_data_int(data[2])
        result = val1 and val2
        # print(f"p10 {val1:x}/{val2:x}/{result:x}")
        return result

    def do_p9_expression(self, data: list):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        # print(f"do_p9_expression count={count} data={data[0]['name']} child={data[0]['child'][0]} ")
        # print(f"xxx {data[0]}")
        val1 = self.get_data_int(data[0])
        # print("xxx 2")
        oper = data[1]
        # print(f"do_p9_expression count={1} data={oper}")
        # print(f"do_p9_expression count={2} data={data[2]['name']} child={data[2]['child']} ")
        val2 = self.get_data_int(data[2])
        result = 0
        if '==' == oper or '=' == oper:
            result = val1 == val2
        else:  # <> or !=
            result = val1 != val2
        if result:
            return 1
        return 0

    def do_p8_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        oper = data[1]
        val2 = self.get_data_int(data[2])
        result = 0
        if '<' == oper:
            result = val1 < val2
        elif '<=' == oper:
            result = val1 <= val2
        elif '>' == oper:
            result = val1 > val2
        else:  # '>='
            result = val1 >= val2
        if result:
            return 1
        return 0

    def do_p7_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        # oper = data[1]
        val2 = self.get_data_int(data[2])
        result = val1 | val2
        # print(f"p7 oper={oper}")
        return result

    def do_p6_expression(self, data):
        # print(f"p6 d={data}")
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        # oper = data[1]
        val2 = self.get_data_int(data[2])
        result = val1 ^ val2
        # print(f"p6 oper={oper} {val1:x}/{val2:x}/{result:x}")
        return result

    def do_p5_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        val2 = self.get_data_int(data[2])
        result = val1 & val2
        # print(f"p5 {val1:x}/{val2:x}/{result:x}")
        return result

    def do_p4_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        oper = data[1]
        val2 = self.get_data_int(data[2])
        result = 0
        if '>>>' == oper:
            result = val1 >> val2
        elif '>>' == oper:
            result = val1 >> val2
        elif '<<' == oper:
            result = val1 << val2
        return result

    def do_p3_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        oper = data[1]
        val2 = self.get_data_int(data[2])
        result = 0
        if '+' == oper:
            result = val1 + val2
        elif '-' == oper:
            result = val1 - val2
        return result

    def do_p2_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[0])
        oper = data[1]
        val2 = self.get_data_int(data[2])
        result = 0
        if '*' == oper:
            result = val1 * val2
        elif '/' == oper:
            result = val1 // val2
        elif '%' == oper:
            result = val1 % val2
        return result

    def do_p1_expression(self, data):
        count = len(data)
        if count == 1:
            return self.get_data(data[0])
        val1 = self.get_data_int(data[1])
        if 0 == val1:
            return 1
        return 0

    def do_int_expression_context(self, data_list):
        count = len(data_list)
        if count == 1:
            return self.get_data(data_list[0])
        else:
            # ()表現=data_list[0]には'('が入っている
            return self.get_data(data_list[1])

    def do_str_expression_context(self, data_list):
        return self.get_data(data_list[0])

    def do_str_context(self, data_list):
        # print(f"str={data_list}")
        result = ''
        for data in data_list:
            state = 0
            old = ''
            for i in range(len(data)):
                hit_flag = False
                ch0 = data[i]
                # print(f"\tch0={ch0}")
                if state == 0:
                    if ch0 == "'":
                        state = 1
                        hit_flag = True
                    elif ch0 == '"':
                        state = 2
                        hit_flag = True
                    elif ch0 == '#':
                        hit_flag = True
                    else:
                        old = old + ch0
                    if hit_flag:
                        result = result + self.get_chr_sharp_str(old)
                        old = ''  # clear
                        if ch0 == '#':
                            old = ch0
                elif state == 1:
                    if ch0 == "'":
                        state = 0
                    else:
                        result = result + ch0
                elif state == 2:
                    if ch0 == '"':
                        state = 0
                    else:
                        result = result + ch0
            result = result + self.get_chr_sharp_str(old)
        # print(f"result={result}")
        return result

    def get_chr_sharp_str(self, base) -> str:
        if len(base) <= 0:
            return ''
        #
        # print(f"\tbaseB={base}")
        if '#' == base[0]:
            # print(f"\tbaseC={base} data={base[1:]}")
            base = self.get_chr_sharp(self.get_ascii_num(base[1:]))
            # print(f"\tbaseD={base} data={base[1:]}")
        elif '$' == base[0]:
            base = self.get_ascii_num(base)
        return base

    def get_chr_sharp(self, data: int) -> str:
        if data <= 0:
            return chr(data & 0xFF)
        result = ''
        while 0 < data:
            result = chr(data & 0xFF) + result
            data = data >> 8
        return result

    def get_sharp_chr(self, data: str) -> int:
        # print(f"getSharpChr {data}")
        if len(data) <= 0:
            return ''
        result = 0
        while '' != data:
            result = (result * 256) + ord(data[0])
            data = data[1:]
        return result

    def int_context(self, data_list) -> int:
        result = 0
        data = data_list[0]
        # print(f"int_context={data}")
        if 0 < len(data) and data[0] == '$':
            result = self.get_ascii_num(data)
        else:
            result = int(data)
        return result

    def get_ascii_num(self, data: str) -> int:
        # print(f"getAsciiNum={data} len={len(data)} data[0]={data[0]}")
        if (0 < len(data)) and ('$' == data[0]):
            ans = int(data[1:], 16)
            # print(f"data[1:]={data[1:]} ans={ans}")
            return ans
        return int(data)

    def do_assert(self, command_name: str, line: int, data_list) -> str:
        ''' assert '''
        message = self.print_command(command_name, line, data_list)
        p1 = self.get_data(data_list[0])
        if p1 == 0:
            raise TypeError(message)

    def do_bplusrecv(self, command_name: str, line: int):
        '''bplusrecv'''
        self.print_command(command_name, line, [])

    def do_bplussend(self, command_name: str, line: int, p1):
        '''bplussend'''
        self.print_command(command_name, line, [p1])

    def do_callmenu(self, command_name: str, line: int, p1):
        '''callmenu'''
        self.print_command(command_name, line, [p1])

    def do_changedir(self, p1):
        '''changedir'''
        p1 = pathlib.Path(p1)
        if p1.is_absolute():
            # print(f"pathA={p1}")
            os.chdir(p1)
        else:
            # print(f"pathB={p1}")
            p1 = pathlib.Path.cwd() / p1
            os.chdir(p1)

    def do_clearscreen(self, command_name: str, line: int, p1):
        '''clearscreen'''
        self.print_command(command_name, line, [p1])

    def do_connect(self, data: str, line):
        '''connect'''
        # print(f"do connect data={data}")
        if self.client is not None:
            self.set_value('error', 'Already connected')
            self.set_value('result', 0)
            return
        param_list = re.split(r"[ \t]+", data)
        server = 'localhost'
        user = None
        passwd = None
        keyfile = None
        com_key = None
        port_number = None
        param_cmd = False
        telnet = False
        telnet_t = 0
        for param in param_list:
            if len(param) <= 0:
                continue
            if param[0] != '/':
                server = param.split(':')
                if len(server) == 1:
                    server = server[0]
                elif len(server) == 2:
                    port_number = int(server[1])
                    server = server[0]
                else:
                    self.set_value('error', 'Invalid server name')
                    self.set_value('result', 0)
                    return
            else:
                user_string = 'user='
                passwd_string = 'passwd='
                keyfile_string = 'keyfile='
                com_string = 'C='
                param = param[1:]
                # print(f"\tparam={param}")
                if "ssh" == param:
                    pass
                elif '1' == param:
                    self.set_value('error', 'SSH1 not support')
                    self.set_value('result', 0)
                    return
                elif '2' == param:
                    pass  # SSH2
                elif 'cmd' == param:
                    param_cmd = True
                elif 't=0' == param.lower():
                    telnet_t = 0
                elif 't=1' == param.lower():
                    telnet_t = 1
                elif 'nossh' == param.lower():
                    telnet = True
                elif 'ask4passwd' == param:
                    self.set_value('error', 'Not Support ask4passwd error!')
                    self.set_value('result', 0)
                    return
                elif 'auth=password' == param:
                    pass  # わからん
                elif 'auth=publickey' == param:
                    pass  # わからん
                elif 'auth=challenge' == param:
                    pass  # わからん
                elif re.search('^' + user_string, param):
                    user = param[len(user_string):]
                elif re.search('^' + passwd_string, param):
                    passwd = param[len(passwd_string):]
                elif re.search('^' + keyfile_string, param):
                    keyfile = param[len(keyfile_string):]
                    keyfile = self.normpath(keyfile)
                elif re.search('^' + com_string, param):
                    com_key = param[len(com_string):]
                    com_key = self.normpath(com_key)
                else:
                    # 知らないパラメータが来たら停止する
                    self.set_value('error', f"unkown paramater={param}")
                    self.set_value('result', 0)
                    return
        #
        # 前の接続は削除
        self.close_client()
        #
        if port_number is None:  # オプションで変えていない場合
            if telnet:
                port_number = 23
            else:
                port_number = 22

        #
        # ここから接続処理
        if com_key is not None:
            try:
                self.shell = MySerial(
                    com_key, self.speed,
                    flowctrl=self.flowctrl,
                    flowctrl_dtr=self.flowctrl_dtr,
                    flowctrl_rts=self.flowctrl_rts)
                self.set_value('result', 2)
            except Exception as e:
                self.set_value('error', f"### l={line} {type(e).__name__} e={e}")
                self.set_value('result', 0)
                self.close_client()
        elif telnet:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((server, port_number))
                if telnet_t == 0:
                    self.shell = MyTelnetT0(client)
                else:
                    self.shell = MyTelnetT1(client)
                self.set_value('result', 2)
            except Exception as e:
                self.set_value('error', f"### l={line} {type(e).__name__} e={e}")
                self.set_value('result', 0)
                self.close_client()
        elif not param_cmd:
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #
                # print(f"p1 {server}, port={port_number}, username={user}, password={passwd}, key_filename={keyfile}")
                self.client.connect(
                    server,
                    port=port_number,
                    username=user,
                    password=passwd,
                    key_filename=keyfile,
                )
                # print(f"p2 {server}, port={port_number}, username={user}, password={passwd}, key_filename={keyfile}")
                #
                self.shell = self.client.invoke_shell()
                if self.shell is None:
                    raise paramiko.SSHException("shell is None")
                # print(f"p3 {server}, port={port_number}, username={user}, password={passwd}, key_filename={keyfile}")
                #
                # 接続成功
                #
                self.set_value('result', 2)
                self.log_connect_time = time.time()
                # print("connect OK !")
                #
            except (
                socket.gaierror,
                paramiko.ssh_exception.NoValidConnectionsError,
                paramiko.AuthenticationException,
                paramiko.SSHException,
            ) as e:
                self.set_value('error', f"### l={line} {type(e).__name__} e={e}")
                self.set_value('result', 0)
                self.close_client()
        else:
            if platform.system().lower() == "linux":
                # ここから expect 起動
                self.shell = MyPexpect()
            else:
                # ここから cmd 起動
                self.shell = MyShell()
            #
            # 接続成功
            self.set_value('result', 2)

    def do_dispstr(self, data_list):
        for data in data_list:
            result = self.get_data(data)
            if isinstance(result, int):
                result = chr(data & 0xFF)
            self.set_log_inner(result)

    def do_enablekeyb(self, command_name: str, line: int, p1):
        '''enablekeyb'''
        pass

    def do_flushrecv(self):
        '''flushrecv'''
        # すでに読んだものを空にする
        self.stdout = ''
        #
        # まだ読めてないものを空にする
        while not self.end_flag:
            #
            local_ssh = self.shell
            if local_ssh is None:
                break
            #
            if not local_ssh.recv_ready():
                break
            #
            output = local_ssh.recv(1024).decode('utf-8', errors='xmlcharrefreplace')
            if output is None:
                break
            output = self.split_escape(output)  # escape文字を吹き飛ばす
            self.set_log_inner(output)

    def do_getmodemstatus(self, p1):
        '''getmodemstatus'''
        # print(f"{p1}")
        if self.shell is None or not isinstance(self.shell, MySerial):
            self.set_value(p1, 0)
            self.set_value('result', 0)
        else:
            self.set_value(p1, self.shell.getmodemstatus())
            self.set_value('result', 1)

    def do_gethostname(self, p1):
        '''gethostname'''
        if self.client is not None and self.shell is not None and self.shell.active:
            # 外部と接続しているとき
            ip_address = self.client.get_transport().getpeername()[0]
            self.set_value(p1, ip_address)
        else:
            #
            # 何もリンクしていない、または cmdと接続しているとき
            hostname = socket.gethostname()
            self.set_value(p1, hostname)

    def get_title(self) -> str:
        '''get title'''
        return self.title

    def do_logautoclosemode(self, name, line, p1):
        self.do_command_context(name, line, (p1))

    def do_logclose(self):
        log_file_handle = self.log_file_handle
        self.log_file_handle = None
        if log_file_handle is not None:
            try:
                log_file_handle.close()
            except Exception:
                pass
        #
        # 他も初期化する
        self.log_start = True
        self.log_timestamp_type = -1
        self.log_connect_time = None

    def do_loginfo(self, name, line, p1):
        self.do_command_context(name, line, (p1))

    def do_logopen(
        self,
        filename,
        binary_flag,
        append_flag,
        plain_text_flag,
        timestamp_flag,
        hide_dialog_flag,
        include_screen_buffer_flag,
        timestamp_type,
    ):
        '''open the log'''
        # 開いているものがあったらクローズする
        self.do_logclose()
        #
        filename = self.normpath(filename)
        #
        option = 'wb'
        # print(f"append_flag={append_flag}")
        if append_flag != 0:
            option = 'ab'
        if binary_flag != 0:
            # plain_text_flag = 0
            timestamp_flag = 0
        if timestamp_flag == 0:
            timestamp_type = -1
        #
        # タイムスタンプの変数を入れる
        self.log_timestamp_type = timestamp_type
        #
        self.log_file_handle = open(filename, option)
        #
        # タイムスタンプありなら最初に書き込む
        if self.log_timestamp_type != -1:
            self.log_file_handle.write(self.get_timestamp().encode('utf-8'))

    def do_logpause(self):
        self.log_start = False

    def do_logrotate(self, name, line, p1, p2):
        '''logrotate'''
        self.do_command_context(name, line, (p1, p2))

    def do_logstart(self):
        self.log_start = True

    def do_logwrite(self, strvar: str):
        ''' logwrite '''
        if self.log_file_handle is None:
            # ログが開かれていない
            return
        #
        if self.log_timestamp_type == -1:
            # タイムスタンプは不要
            if isinstance(strvar, str):
                strvar = strvar.encode('utf-8')
            self.log_file_handle.write(strvar)
        else:
            # タイムスタンプを付ける必要がある
            while True:
                if strvar == '':
                    break
                index = strvar.find("\n")
                if index < 0:
                    if isinstance(strvar, str):
                        strvar = strvar.encode('utf-8')
                    self.log_file_handle.write(strvar)
                    break
                target = strvar[: index + 1]
                if isinstance(target, str):
                    target = target.encode('utf-8')
                self.log_file_handle.write(target)
                self.log_file_handle.write(self.get_timestamp().encode('utf-8'))
                strvar = strvar[index + 1:]

    def get_timestamp(self) -> str:
        '''get timestamp from log_timestamp_type'''
        if self.log_timestamp_type == 0:
            # ローカルタイム
            return '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']'
        elif self.log_timestamp_type == 1:
            # UTC
            return '[' + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S') + ']'
        elif self.log_timestamp_type == 2:
            # 経過時間 (Logging)
            return self.get_timestamp_elapsed(self.log_login_time)
        else:
            # 経過時間 (Connection)
            return self.get_timestamp_elapsed(self.log_connect_time)

    def get_timestamp_elapsed(self, start) -> str:
        '''get Elapsed Timestamp'''
        total_seconds = 0
        if start is not None:
            total_seconds = int(start - time.time())
        day = total_seconds // (60 * 60 * 24)
        hours = (total_seconds // (60 * 60)) % 24
        minutes = (total_seconds // 60) % 3600
        seconds = total_seconds % 60
        return f"[{day} {hours:02}:{minutes:02}:{seconds:02}]"

    def do_recvln(self):
        '''recvln'''
        result_list = ["\n"]
        self.invoke_wait(result_list)

    def do_scprecv(self, p1, p2):
        '''SCP 受信'''
        if self.client is None:
            return
        sftp_connection = self.client.open_sftp()
        sftp_connection.get(p1, p2)
        sftp_connection.close()

    def do_scpsend(self, p1, p2):
        '''SCP 転送'''
        if self.client is None:
            return
        sftp_connection = self.client.open_sftp()
        sftp_connection.put(p1, p2)
        sftp_connection.close()

    def do_send(self, data_list):
        '''send'''
        # print(f"do_send() d={data_list}")
        for data in data_list:
            result = self.get_data(data)
            self.invoke_send(result)

    def do_sendbreak(self):
        '''sendbrake'''
        # print(f"do_sendbreak() d={data_list}")
        self.invoke_send("\x03")

    def do_sendln(self, data_list):
        '''sendln'''
        # print(f"do_sendln() d={data_list}")
        if len(data_list) <= 0:
            self.invoke_send("\n")
        else:
            for data in data_list:
                message = self.get_data(data)
                self.invoke_send(message + "\n")

    def do_setspeed(self, p1):
        '''setspeed'''
        self.speed = p1

    def do_setecho(self, line, p1):
        '''setecho'''
        if p1 != 0:
            raise TypeError(f"## l={line} Unsupport exception echo!=0")

    def do_setflowctrl(self, p1):
        '''setflowctrl'''
        self.flowctrl = p1

    def do_setdtr(self, p1):
        '''setdtr'''
        self.flowctrl_dtr = p1 != 0

    def do_setrts(self, p1):
        '''setrts'''
        self.flowctrl_rts = p1 != 0

    def invoke_send(self, message):
        '''sendall'''
        #
        # send 前に来たものを読み捨てる
        self.do_flushrecv()
        #
        # print(f"invoke_send d={message}")
        while not self.end_flag:
            local_shell = self.shell
            if local_shell is None:
                # print("invoke_send shell None")
                break
            elif local_shell.send_ready():
                # print(f"send! f=/{message}/")
                local_shell.send(message)
                break
            else:
                time.sleep(0.1)

    def set_title(self, title: str):
        '''set title'''
        self.title = title

    def do_testlink(self):
        '''testlink'''
        if self.shell is None or not self.shell.active:
            self.set_value('result', 0)
        else:
            self.set_value('result', 2)

    def do_wait(self, data_list):
        '''wait'''
        result_list = []
        for data in data_list:
            result = self.get_data(data)
            result_list.append(result)
        self.invoke_wait(result_list)

    def do_waitln(self, data_list):
        '''waitln'''
        result_list = []
        for data in data_list:
            result = self.get_data(data) + "\n"
            result_list.append(result)
        self.invoke_wait(result_list)

    def invoke_wait(self, result_list):
        # print(f"invoke_wait x=/{result_list}/")
        m_timeout = self.get_timer()
        now_time = time.time()
        result = 0
        hit_flag = False
        self.set_value('result', 0)
        while not self.end_flag and not hit_flag:
            #
            if m_timeout != 0:
                r_time = (now_time + m_timeout) - time.time()
                # print(f"\ninvoke_wait {r_time} / {m_timeout}")
                if r_time < 0:
                    result = 0  # timeout
                    # print(f"hit1! {r_time}")
                    break
            #
            # 生成したものでヒットするか確認
            result = 1
            max = None
            result_len = ""
            #
            # 全件チェックする
            for i, reslut_text in enumerate(result_list):
                index = self.stdout.find(reslut_text)
                if 0 <= index:
                    hit_flag = True
                    if max is None or index < max:
                        # 最初にヒットしたか、より最初にヒットする方を選ぶ
                        max = index
                        result_len = len(reslut_text)
                        result = i + 1
            #
            if hit_flag:
                # 見つかった地点まで切り飛ばす
                # print(f"remain1=/{self.stdout}/ cutlen={max + result_len}")
                self.stdout = self.stdout[max + result_len:]
                # print(f"remain2=/{self.stdout.strip()}/")
                self.set_value('result', result)
                # ヒットしていたら終了
                break
            #
            local_ssh = self.shell
            if local_ssh is None:
                break
            #
            # m_timeout は 0 の時無限待ちになる
            if local_ssh.recv_ready():
                now_time = time.time()  # 最後の時間更新
                # print("recv start! ============")
                output = local_ssh.recv(1024)
                # print(f"recv! end {output} ============")
                if output is None:
                    break
                output = output.decode('utf-8', errors='xmlcharrefreplace')
                output = self.split_escape(output)  # escape文字を吹き飛ばす
                self.set_log_inner(output)
                self.stdout = self.stdout + output
                #
            else:
                # print("sleep")
                time.sleep(0.1)

    def get_timer(self) -> float:
        m_timeout = 0.0
        x = self.get_value('timeout', error_stop=False)
        if x is not None:
            m_timeout = int(x)
        x = self.get_value('mtimeout', error_stop=False)
        if x is not None:
            m_timeout = m_timeout + (int(x) / 1000)
        return m_timeout

    def do_call(self, line, label):
        #
        try:
            self.do_goto_context(line, label)
        except TtlReturnFlagException:
            pass

    def do_pause(self, p1):
        '''pause'''
        # print(f"pause {p1}")
        if self.end_flag:
            return

        # 1秒未満の待ち
        mtime = p1 - int(p1)
        if 0 < mtime:
            time.sleep(mtime)

        # 1秒以上の待ちは1秒づつ end_flagが立っていないか見る
        for ignore in range(int(p1)):
            if self.end_flag:
                break
            time.sleep(1)

    def do_code2str(self, p1, p2):
        if p2 == 0:
            self.set_value(p1, '')
        else:
            p2 = self.get_chr_sharp(p2)
            self.set_value(p1, p2)

    def do_expandenv(self, p1, p2):
        if platform.system().lower() != 'linux':
            p2 = os.path.expandvars(p2)
        else:
            pattern = r"%(.*?)%"
            p2 = re.sub(pattern, lambda match: f"%{match.group(1).lower()}%", p2)
            p2 = p2.replace('%windir%', 'c:\\windows')
            p2 = p2.replace('%systemroot%', '/root')
            p2 = p2.replace('%programfiles%', '/usr/local')
            p2 = p2.replace('%programfiles(x86)%', '/usr/local')
            p2 = p2.replace('%userprofile%', os.environ.get('HOME'))
            p2 = p2.replace('%appdata%', '/usr/local')
            p2 = p2.replace('%localappdata%', '/usr/local')
            p2 = p2.replace('%temp%', '/tmp')
            p2 = p2.replace('%tmp%', '/tmp')
            p2 = p2.replace('%computerprogramfiles%', '/usr/local')
            p2 = p2.replace('%public%', os.environ.get('HOME'))
            p2 = p2.replace('%computername%', socket.gethostname())
            p2 = p2.replace('%username%', getpass.getuser())
            p2 = p2.replace('%path%', os.environ.get('PATH'))
        #
        self.set_value(p1, p2)

    def do_sprintf(self, inputstr, data_line):
        format = self.get_data(data_line[0])
        data_new = []
        for data in data_line[1:]:
            data_new.append(self.get_data(data))
        # print(f"format={format}")
        # print(f"data_new={tuple(data_new)}")
        strvar = format % tuple(data_new)
        # print(f"strvar={strvar}")
        self.set_value(inputstr, strvar)
        self.set_value('result', 0)

    def do_str2code(self, p1, p2):
        p2 = self.get_sharp_chr(p2)
        self.set_value(p1, p2)

    def do_strcompare(self, p1, p2):
        result = 0
        if p1 == p2:
            result = 0
        elif p1 < p2:
            result = -1
        else:
            result = 1
        self.set_value('result', result)

    def do_strconcat(self, p1, p2):
        p1_str = self.get_value(p1)
        p1_str = p1_str + p2
        self.set_value(p1, p1_str)

    def do_strcopy(self, p1, p2, p3, p4):
        p2 = p2 - 1  # 1オリジン
        if p2 < 0:
            p2 = 0
        p1 = p1[p2: p2 + p3]
        self.set_value(p4, p1)

    def do_strinsert(self, p1, p2, p3):
        p2 = p2 - 1  # 1オリジン
        p1_val = self.get_data(p1)
        # print(f"### l={line} {command_name} {p1} {p2} {p3} {p1_val}")
        p1_val = p1_val[:p2] + p3 + p1_val[p2:]
        self.set_value(p1, p1_val)

    def do_strjoin(self, p1, p2, p3):
        p1_val = ''
        for i in range(p3):
            if i != 0:
                p1_val = p1_val + p2
            p1_val = p1_val + self.get_value('groupmatchstr' + str(i + 1))
        self.set_value(p1, p1_val)

    def do_strlen(self, p1):
        self.set_value('result', len(p1))

    def do_strmatch(self, target_string, string_with_regular_expressio):
        # print(f"strmatch {target_string} {string_with_regular_expressio}")
        match = re.search(string_with_regular_expressio, target_string)
        if match:
            # print(f"hit strmatch {target_string} {string_with_regular_expressio}")
            self.set_value('result', match.start() + 1)
            i = 0
            for grp in match.groups():
                self.set_value('groupmatchstr' + str(i + 1), grp)
                i = i + 1
                if 10 <= i:
                    break
        else:
            self.set_value('result', 0)

    def do_strremove(self, p1, p2, p3):
        p2 = p2 - 1  # 1オリジン
        p1_val = self.get_data(p1)
        # print(f"### l={line} {command_name} {p1} {p2} {p3} {p1_val}")
        p1_val = p1_val[:p2] + p1_val[p2 + p3:]
        self.set_value(p1, p1_val)

    def do_strreplace(self, strvar, index, regex, newstr):
        strvar_val = self.get_data(strvar)
        index = index - 1  # 1オリジン
        strvar_pre = strvar_val[0:index]
        strvar_val = strvar_val[index:]
        strvar_val = strvar_pre + re.sub(regex, newstr, strvar_val)
        try:
            self.set_value(strvar, strvar_val)
            self.set_value('result', 1)
        except (re.error, TypeError, ValueError):
            self.set_value('result', 0)

    def do_strscan(self, p1, p2):
        index = p1.find(p2)
        if index < 0:
            index = 0
        else:
            index = index + 1
        # print(f"strscan {index}")
        self.set_value('result', index)

    def do_strsplit(self, p1, p2, p3):
        p1_val = self.get_data(p1)
        for i in range(9):
            self.set_value('groupmatchstr' + str(i + 1), '')
        i = 0
        while i < p3 - 1:
            index = p1_val.find(p2)
            if 0 <= index:
                # print(f"aa i{i + 1} {p3} /{p1_val[0:index]}/ /{p1_val[index + len(p2):]}/")
                self.set_value('groupmatchstr' + str(i + 1), p1_val[0:index])
                p1_val = p1_val[index + len(p2):]
            else:
                break
            i = i + 1
        if 0 < len(p1_val):
            # print(f"bb i{i + 1} {p3} /{p1_val}/")
            self.set_value('groupmatchstr' + str(i + 1), p1_val)
        i = i + 1
        # print(f"i={i}")
        self.set_value('result', i)

    def do_strspecial(self, p1, p2):
        value = ''
        if p2 is None:
            value = self.get_data_str(p1)
        else:
            value = p2
        value = value.encode().decode('unicode_escape', errors='xmlcharrefreplace')
        self.set_value(p1, value)

    def do_strtrim(self, p1: str, p2: str):
        '''strtrim'''
        p1_var = self.get_data(p1)
        # エスケープを変換する
        p2 = p2.encode().decode('unicode_escape', errors='xmlcharrefreplace')

        # 前方方向
        while 0 < len(p1_var):
            ch = p1_var[0]
            if ch not in p2:
                break
            p1_var = p1_var[1:]

        # 後方方向
        while 0 < len(p1_var):
            ch = p1_var[-1]
            if ch not in p2:
                break
            p1_var = p1_var[:-1]
        self.set_value(p1, p1_var)

    def do_basename(self, p1, p2):
        p2 = self.normpath(p2)
        # print(f"p2a={p2}")
        p2 = re.sub(r'[\/]$', '', p2)
        p2 = pathlib.Path(p2)
        # print(f"p2b={p2}")
        p2 = str(p2.parent)
        # print(f"p2c={p2}")
        self.set_value(p1, str(p2))

    def do_fileclose(self, file_handle):
        '''fileclose'''
        if file_handle not in self.file_handle_list:
            return
        file_handle_base = self.file_handle_list[file_handle]
        #
        self.file_handle_list[file_handle] = None
        del self.file_handle_list[file_handle]
        #
        file_handle_file = file_handle_base['file_handle']
        if file_handle_file is None:
            return
        try:
            self.file_handle.close()
        except Exception:
            pass

    def do_fileconcat(self, p1, p2):
        p1 = self.normpath(p1)
        p2 = self.normpath(p2)
        if p1 == p2:
            self.set_value('result', 0)
            return
        try:
            with open(p1, 'ab') as f1:
                with open(p2, 'rb') as f2:
                    f1.write(f2.read())
            self.set_value('result', 1)
        except OSError:
            self.set_value('result', 0)

    def do_filecopy(self, p1, p2):
        p1 = self.normpath(p1)
        p2 = self.normpath(p2)
        if p1 == p2:
            self.set_value('result', 0)
            return
        try:
            with open(p1, 'rb') as f1:
                with open(p2, 'wb') as f2:
                    f2.write(f1.read())
            self.set_value('result', 1)
        except OSError:
            self.set_value('result', 0)

    def do_filedelete(self, filename):
        filename = self.normpath(filename)
        if not os.path.exists(filename):
            self.set_value('result', 0)
            return
        try:
            os.remove(filename)
            self.set_value('result', 1)
        except OSError:
            self.set_value('result', 0)

    def do_fileopen(
        self, file_handle, filename: str, append_flag: int, readonly_flag: int
    ):
        '''fileopen'''
        if file_handle in self.file_handle_list:
            self.do_fileClose(file_handle)
        filename = self.normpath(filename)
        self.file_handle_list[file_handle] = {}
        self.file_handle_list[file_handle]['file_handle'] = None
        self.file_handle_list[file_handle]['filename'] = filename
        self.file_handle_list[file_handle]['append_flag'] = append_flag
        self.file_handle_list[file_handle]['readonly_flag'] = readonly_flag
        self.get_value('result', 0)

    def do_filereadln(self, line, file_handle, strvar):
        file_handle_file = self.get_openhandle(line, file_handle)
        #
        try:
            text = file_handle_file.readline()
            text = text.decode('utf-8', errors='xmlcharrefreplace')
            text = text.rstrip("\n").rstrip("\r")
            self.set_value(strvar, text)
            self.set_value('result', 0)
        except OSError:
            self.set_value(strvar, '')
            self.set_value('result', 1)

    def do_fileread(self, line, file_handle, read_byte, strvar):
        file_handle_file = self.get_openhandle(line, file_handle)
        #
        text = file_handle_file.read(read_byte)
        if text is not None:
            self.set_value(strvar, text.decode('utf-8', errors='xmlcharrefreplace'))
            self.set_value('result', 1)
        else:
            self.set_value(strvar, '')
            self.set_value('result', 0)

    def do_filerename(self, p1, p2):
        p1 = self.normpath(p1)
        p2 = self.normpath(p2)
        # print(f"do_filerename0 {p1} {p2}")
        if p1 == p2:
            # print(f"do_filerename1 {p1} {p2}")
            self.set_value('result', 1)
            return
        if not os.path.exists(p1):
            # print(f"do_filerename2 {p1} {p2}")
            self.set_value('result', 1)
            return
        self.do_filedelete(p2)
        try:
            os.rename(p1, p2)
            self.set_value('result', 0)
        except OSError:
            self.set_value('result', 1)

    def do_filesearch(self, filename):
        filename = self.normpath(filename)
        if os.path.exists(filename):
            self.set_value('result', 1)
        else:
            self.set_value('result', 0)

    def do_filestat(self, filename, size, mtime, drive):
        try:
            filename = self.normpath(filename)
            size_val = os.path.getsize(filename)
            self.set_value(size, size_val)
            if mtime is not None:
                timestamp = os.path.getmtime(filename)
                dt = datetime.fromtimestamp(timestamp)
                self.set_value(mtime, dt)
            if drive is not None:
                drive_val, xx = os.path.splitdrive(filename)
                self.set_value(drive, drive_val)
            self.set_value('result', 0)
        except FileNotFoundError:
            self.set_value(size, 0)
            if mtime is not None:
                self.set_value(mtime, '')
            if drive is not None:
                self.set_value(drive, '')
            self.set_value('result', -1)

    def do_filetruncate(self, filename: str, size: int):
        size_val = 0
        try:
            filename = self.normpath(filename)
            size_val = os.path.getsize(filename)
        except FileNotFoundError:
            self.set_value(size, 0)
            size_val = 0
        if size_val == size:
            return
        try:
            if size < size_val:
                # 切り詰めが必要
                with open(filename, 'r+b') as f:
                    fd = f.fileno()
                    os.truncate(fd, size)
            else:
                # ゼロバイト加算
                with open(filename, 'ab') as f:
                    f.write(bytes(size - size_val))
        except OSError:
            self.set_value('result', -1)

    def do_filewrite(self, line, file_handle, data):
        if file_handle not in self.file_handle_list:
            raise TypeError(f"### l={line} file_handle not found f={file_handle}")
        file_handle_base = self.file_handle_list[file_handle]
        file_handle_file = file_handle_base['file_handle']
        if file_handle_file is None:
            option = 'wb'
            if file_handle_base['append_flag'] != 0:
                option = 'ab'
            file_handle_file = open(file_handle_base['filename'], option)
            file_handle_base['file_handle'] = file_handle_file
        file_handle_file.write(data.encode('utf-8'))

    def get_openhandle(self, line, file_handle):
        if file_handle not in self.file_handle_list:
            raise TypeError(f"### l={line} file_handle not found f={file_handle}")
        file_handle_base = self.file_handle_list[file_handle]
        file_handle_file = file_handle_base['file_handle']
        if file_handle_file is None:
            file_handle_file = open(file_handle_base['filename'], 'rb')
            file_handle_base['file_handle'] = file_handle_file
        return file_handle_file

    def do_findfirst(self, line, file_handle, file_name: str, strvar: str):
        '''findfirst'''
        if file_handle in self.file_handle_list:
            self.do_fileClose(file_handle)
        self.file_handle_list[file_handle] = {}
        self.file_handle_list[file_handle]['file_handle'] = MyFindfirst(file_name)
        self.file_handle_list[file_handle]['filename'] = file_name
        self.file_handle_list[file_handle]['append_flag'] = False
        self.file_handle_list[file_handle]['readonly_flag'] = True
        self.do_findnext(line, file_handle, strvar)

    def do_findnext(self, line, file_handle, strvar: str):
        '''findnext'''
        self.do_filereadln(line, file_handle, strvar)
        if self.get_value('result') == 0:
            self.set_value('result', 1)
        else:
            self.set_value('result', 0)

    def do_foldercreate(self, folder_name):
        try:
            folder_name = self.normpath(folder_name)
            os.mkdir(folder_name)
            self.set_value('result', 1)
        except FileNotFoundError:
            self.set_value('result', 0)

    def do_folderdelete(self, folder_path):
        folder_path = self.normpath(folder_path)
        if not os.path.isdir(folder_path):
            self.set_value('result', 0)
            return
        try:
            os.rmdir(folder_path)
            self.set_value('result', 1)
        except OSError:
            self.set_value('result', 0)

    def do_foldersearch(self, folder_path):
        folder_path = self.normpath(folder_path)
        if os.path.isdir(folder_path):
            self.set_value('result', 1)
        else:
            self.set_value('result', 0)

    def do_makepath(self, strvar, dir, name):
        dir = self.normpath(dir)
        result = os.path.abspath(dir)
        result = os.path.join(result, name)
        self.set_value(strvar, result)

    def do_delpassword(self, filename: str, password_name: str):
        # print(f"do_getpassword p3={p3}")
        filename = self.normpath(filename)
        worker = self.get_encrypt_file(filename)
        # print(f"do_getpassword worker={worker}")
        if password_name in worker:
            del worker[password_name]
        self.set_encrypt_file(filename, worker)

    def do_getpassword(
        self, filename: str, password_name: str, p3: str, encrypt_str: str
    ):
        # print(f"do_getpassword p3={p3}")
        filename = self.normpath(filename)
        worker = self.get_encrypt_file(filename)
        # print(f"do_getpassword worker={worker}")
        if password_name in worker and 2 <= len(worker[password_name]):
            encrypt_byte = encrypt_str.encode('utf-8')
            encrypt_byte = encrypt_byte.ljust(32, b"\0")  # 32byte以下なら増やす
            encrypt_byte = encrypt_byte[:32]  # 32byte以上を無視する
            encrypt_byte = base64.urlsafe_b64encode(encrypt_byte)
            cipher = Fernet(encrypt_byte)
            #
            # print(f"d {password_name} 0={worker[password_name][0]}")
            target_0 = base64.b64decode(worker[password_name][0].encode())
            target_1 = base64.b64decode(worker[password_name][1].encode())
            try:
                target_0 = cipher.decrypt(target_0).decode('utf-8', errors='xmlcharrefreplace')
                target_1 = cipher.decrypt(target_1).decode('utf-8', errors='xmlcharrefreplace')
            except InvalidToken:
                self.set_value('result', 0)
                return
            # print(f"e {password_name} 0={target_0}")
            # print(f"e {password_name} 0={target_1}")
            #
            if f"{target_0}_{encrypt_str}" == target_1:
                self.set_value(p3, target_0)
                self.set_value('result', 1)
            else:
                # encriptが一致しなかった
                self.set_value('result', 0)
        else:
            self.set_value('result', 0)

    def do_ispassword(self, filename: str, password_name: str):
        # print(f"do_getpassword p3={p3}")
        filename = self.normpath(filename)
        worker = self.get_encrypt_file(filename)
        # print(f"do_getpassword worker={worker}")
        if password_name in worker:
            self.set_value('result', 1)
        else:
            self.set_value('result', 0)

    def do_setpassword(
        self, filename: str, password_name: str, password: str, encrypt_str: str
    ):
        worker = {}
        filename = self.normpath(filename)
        worker = self.get_encrypt_file(filename)
        encrypt_byte = encrypt_str.encode('utf-8')
        encrypt_byte = encrypt_byte.ljust(32, b"\0")  # 32byte以下なら増やす
        encrypt_byte = encrypt_byte[:32]  # 32byte以上を無視する
        encrypt_byte = base64.urlsafe_b64encode(encrypt_byte)
        cipher = Fernet(encrypt_byte)
        #
        target_0 = password.encode('utf-8')  # 文字をセット
        target_1 = f"{password}_{encrypt_str}".encode('utf-8')
        # print(f"d {password_name} {password} 0={target_0}")
        target_0 = cipher.encrypt(target_0)  # byte列に変更して暗号化
        target_1 = cipher.encrypt(target_1)
        target_0 = base64.b64encode(target_0).decode('utf-8', errors='xmlcharrefreplace')  # base64に変更して文字にする
        target_1 = base64.b64encode(target_1).decode('utf-8', errors='xmlcharrefreplace')
        worker[password_name] = [target_0, target_1]
        # print(f"c {password_name} {password}  0={target_0}")
        result = self.set_encrypt_file(filename, worker)
        # print(f"do_setpassword2 str={filename} p={password_name} p={password} w={worker}")
        self.set_value('result', result)
        # print(f"do_setpassword3 str={filename} p={password_name} p={password} w={worker}")

    def set_encrypt_file(self, filename, worker: dict) -> int:
        '''暗号化のファイル書き込み後、学習しておく'''
        # エンコードしたい元の文字列
        original_text = json.dumps(worker)
        filename = self.normpath(filename)
        filename = str(pathlib.Path(filename).resolve())
        self.encrypt_file[filename] = worker
        #
        # ファイルへの書き込み
        try:
            with open(filename, 'wt') as f:
                f.write(original_text)
        except (FileNotFoundError, IOError):
            return 0
        return 1

    def get_encrypt_file(self, filename):
        '''暗号化のファイル読み込みを１回で終わらせる'''
        #
        # すでに読み込んでいるなら、それを使う
        filename = self.normpath(filename)
        filename = str(pathlib.Path(filename).resolve())
        if filename in self.encrypt_file:
            return self.encrypt_file[filename]
        #
        # データがないのでファイルからロードする
        worker = {}
        try:
            with open(filename, 'rt') as f:
                worker = json.loads(f.read())
                self.encrypt_file[filename] = worker
        except (FileNotFoundError, IOError, json.decoder.JSONDecodeError):
            worker = {}
        return worker

    def do_checksum8(self, p1: str, p2: str):
        p2_byte = p2.encode('utf-8')
        self.get_checksum(p1, p2_byte, 0x0F)

    def do_checksum8file(self, p1: str, p2: str):
        self.set_value(p1, 0)  # default value
        try:
            with open(p2, 'rb') as f:
                p2_byte = f.read()
                self.get_checksum(p1, p2_byte, 0x0F)
                self.set_value('result', 0)
        except Exception:
            self.set_value('result', -1)

    def do_checksum16(self, p1: str, p2: str):
        p2_byte = p2.encode('utf-8')
        self.get_checksum(p1, p2_byte, 0xFF)

    def do_checksum16file(self, p1: str, p2: str):
        self.set_value(p1, 0)  # default value
        try:
            with open(p2, 'rb') as f:
                p2_byte = f.read()
                self.get_checksum(p1, p2_byte, 0xFF)
                self.set_value('result', 0)
        except Exception:
            self.set_value('result', -1)

    def do_checksum32(self, p1: str, p2: str):
        p2_byte = p2.encode('utf-8')
        self.get_checksum(p1, p2_byte, 0xFFFF)

    def do_checksum32file(self, p1: str, p2: str):
        self.set_value(p1, 0)  # default value
        try:
            with open(p2, 'rb') as f:
                p2_byte = f.read()
                self.get_checksum(p1, p2_byte, 0xFFFF)
                self.set_value('result', 0)
        except Exception:
            self.set_value('result', -1)

    def get_checksum(self, p1: str, p2_byte, mask: int):
        sum = 0
        for b in p2_byte:
            # print(f"b={int(b):#02x}")
            sum = (sum + int(b)) & mask
        self.set_value(p1, sum)

    def do_crc16(self, p1: str, p2: str):
        p2_byte = p2.encode('utf-8')
        self.get_crc16_IBM_SDLC(p1, p2_byte)

    def do_crc16file(self, p1: str, p2: str):
        self.set_value(p1, 0)  # default value
        try:
            with open(p2, 'rb') as f:
                p2_byte = f.read()
                self.get_crc16_IBM_SDLC(p1, p2_byte)
                self.set_value('result', 0)
        except Exception:
            self.set_value('result', -1)

    def get_crc16_IBM_SDLC(self, p1: str, data: bytes):
        r = 0xFFFF
        for byte in data:
            r = r ^ byte
            for ignore in range(8):
                if r & 0x1 == 1:
                    r = (r >> 1) ^ 0x8408
                else:
                    r = r >> 1
        r = r ^ 0xFFFF
        self.set_value(p1, r)

    def do_crc32(self, p1: str, p2: str):
        p2_byte = p2.encode('utf-8')
        self.get_crc32_IBM_SDLC(p1, p2_byte)

    def do_crc32file(self, p1: str, p2: str):
        self.set_value(p1, 0)  # default value
        try:
            with open(p2, 'rb') as f:
                p2_byte = f.read()
                self.get_crc32_IBM_SDLC(p1, p2_byte)
                self.set_value('result', 0)
        except Exception:
            self.set_value('result', -1)

    def get_crc32_IBM_SDLC(self, p1: str, data: bytes):
        r = 0xFFFFFFFF
        for byte in data:
            r = r ^ byte
            for ignore in range(8):
                if r & 0x1 == 1:
                    r = (r >> 1) ^ 0xEDB88320
                else:
                    r = r >> 1
        r = r ^ 0xFFFFFFFF
        self.set_value(p1, r)

    def do_exec(self, line, data_line):
        # print(f"### l={line} do_exec() ")
        data_len = len(data_line)
        command = self.get_data(data_line[0])
        command_list = re.split(r"[ \t]+", command)
        show = 1  # SW_SHOWNORMAL
        if 2 <= (data_len):
            show = self.get_data(data_line[1]).lower()
            if 'show' == show:
                pass
            elif 'minimize' == show:
                show = 6  # SW_MINIMIZE
            elif 'maximize' == show:
                show = 3  # SW_MAXIMIZE
            elif 'hide' == show:
                show = 0  # SW_HIDE
            else:
                raise TypeError(f"### l={line} do_exec type error")
        wait = 0
        if 3 <= (data_len):
            wait = self.get_data_int(data_line[2])
        base_directory = '.'
        if 4 <= (data_len):
            base_directory = self.get_data(data_line[3])
            if not os.path.isdir(base_directory):
                base_directory = '.'
        # print(f"\tcommand_list={command_list}")
        # print(f"\tshow={show}")
        # print(f"\twait={wait}")
        # print(f"\tbase_directory={base_directory}")
        #
        si = None
        if platform.system().lower() != 'linux':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE
        p = subprocess.Popen(
            command_list, startupinfo=si, cwd=base_directory, shell=True
        )
        if wait != 0:
            p.wait()  # プロセスが終了するまで待機
            self.set_value('result', p.returncode)

    def do_getdate(self, data_line, format='%Y-%m-%d'):
        date = self.get_key_name(data_line[0])
        data_len = len(data_line)
        if 2 <= data_len:
            format = self.get_data(data_line[1])
        #
        local_timezone = None
        # print(f"timezone={local_timezone}")
        if 3 <= data_len:
            local_timezone = self.get_data(data_line[2])
        date_str = ''
        if local_timezone is None:
            local_now = datetime.now()
        else:
            local_now = datetime.now(ZoneInfo(local_timezone))
        date_str = local_now.strftime(format)
        self.set_value(date, date_str)

    def do_getenv(self, p1, p2):
        # print(f"getenv1 c=({command_name}) l={p1} r={p2}")
        p1 = os.getenv(p1)
        if p1 is None:
            p1 = ''
        # print(f"getenv2 c=({command_name}) l={p1} r={p2}")
        self.set_value(p2, p1)

    def do_getipv4addr(self, string_array, intvar):
        ip = socket.gethostbyname(socket.gethostname())
        if ip is None:
            self.set_value(intvar, 0)
            return
        self.set_value(string_array + '[0]', ip)
        self.set_value(intvar, 1)

    def do_getipv6addr(self, string_array, intvar):
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6)
        i = 0
        if infos is None:
            self.set_value(intvar, 0)
            self.set_value('result', 0)
            return
        for info in infos:
            ipv6 = info[4][0]
            # print("IPv6アドレス:", ipv6)
            self.set_value(f"{string_array}[{str(i)}]", ipv6)
            i = i + 1
        self.set_value(intvar, i)
        if 0 < i:
            self.set_value('result', 1)
        else:
            self.set_value('result', 0)

    def do_getver(self, strvar: str, target_version: float):
        '''getver'''
        # print("do_getver")
        now_version = float(VERSION)
        self.set_value(strvar, str(now_version))
        if target_version is not None:
            if now_version == target_version:
                self.set_value('result', 0)
            elif now_version < target_version:
                self.set_value('result', -1)
            else:
                self.set_value('result', 1)
        # print("do_getver end")

    def do_ifdefined(self, strvar: str):
        result = 0
        if strvar in self.value_list:
            # print(f"do_ifdefined /{strvar}/")
            result = self.get_value(strvar)
            if isinstance(result, Label):
                result = 4
            elif isinstance(result, int):
                result = 1
            else:
                result = 3
        else:
            for value in self.value_list:
                # print(f"hit2 {value}/{strvar}")
                if strvar + '[' in value:
                    if isinstance(self.get_value(value), int):
                        result = 5
                    else:
                        result = 6
                    break
            self.set_value('result', 0)
        # print(f"do_ifdefined v={strvar} d={result}")
        self.set_value('result', result)

    def do_setexitcode(self, p1):
        self.exitcode = int(p1)


#
