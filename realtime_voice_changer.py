# -*- coding:utf-8 -*-
#プロット関係のライブラリ
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import sys
#音声関係のライブラリ
import pyaudio
import struct
from scipy import frombuffer,array,int16

class PlotWindow:
    def __init__(self):
        #プロット初期設定
        self.win=pg.GraphicsWindow()
        self.win.setWindowTitle(u"リアルタイムプロット")
        self.plt=self.win.addPlot() #プロットのビジュアル関係
        self.plt.setYRange(-1,1)    #y軸の上限、下限の設定
        self.curve=self.plt.plot()  #プロットデータを入れる場所

        #マイクインプット設定
        self.CHUNK=1024             #1度に読み取る音声のデータ幅
        self.RATE=44100             #サンプリング周波数
        self.audio=pyaudio.PyAudio()
        self.stream=self.audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=self.RATE,
                                    input=True,
                                    output=True,
                                    frames_per_buffer=self.CHUNK)

        #アップデート時間設定
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)    #10msごとにupdateを呼び出し

        #音声データの格納場所(プロットデータ)
        self.data=np.zeros(self.CHUNK)

    def update(self):
        self.data=self.AudioInput()
        self.curve.setData(self.data)   #プロットデータを格納   

    def PitchShift(self,inp,rate):
        outp = []
        for i in range(int(len(inp) / rate)):
            outp.append(inp[int(i * float(rate))])
        for i in range(int(len(inp))-int(len(inp) / rate)):
            outp.append(inp[int(i * float(rate))])
        return array(outp)

    def AudioInput(self):
        ret=self.stream.read(self.CHUNK)    #音声の読み取り(バイナリ)
        ret=frombuffer(ret,dtype = "int16")
        if ret !='':
            ret = self.PitchShift(ret,2)
        self.output = int16(ret).tostring()
        self.output = self.stream.write(ret)
        #バイナリ → 数値(int16)に変換
        #32768.0=2^16で割ってるのは正規化(絶対値を1以下にすること)
        ret=np.frombuffer(ret, dtype="int16")/32768.0
        return ret

if __name__=="__main__":
    plotwin=PlotWindow()
    if(sys.flags.interactive!=1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
