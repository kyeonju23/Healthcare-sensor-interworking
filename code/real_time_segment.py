import mcp3008_emg as ms
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import time


EMG = 0
Envelope = 1

mcp_emg = ms.set_mcp(EMG)
mcp_env = ms.set_mcp(Envelope)

class Scope(object):
    
    # 초기 설정
    # X-axis setting
    def __init__(self,
                 ax,fn,
                 xmax=5,ymax =200,
                 xstart=0, ystart=120,
                 title='Real Time EMG Signal',xlabel='Time(sec)',ylabel='EMG(V)'):
        
        self.xmax = xmax #x축 길이
        self.xstart = xstart #x축 시작점
        self.ymax = ymax #y축 길이
        self.ystart = ystart #y축 시작점
        
        # 그래프 설정
        self.ax = ax 
        self.ax.set_xlim((self.xstart,self.xmax))
        self.ax.set_ylim((self.ystart,self.ymax))
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        self.x = [0] # x축 정보 
        self.y = [0] # y축 정보
        self.value = 0 # 축 값
        self.fn = fn
        self.line, = ax.plot([],[],color='darkBlue')
        self.ti = time.time() #현재시각
        print("초기화 완료")

    # 그래프 설정
    def update(self, i):
        # 시간차
        tempo = time.time()-self.ti
        self.ti = time.time() #시간 업데이트
        
        # 값 넣기
        self.value = self.fn()# y값 함수 불러오기
        self.y.append(self.value) #y값 넣기
        self.x.append(tempo + self.x[-1]) #x값 넣기
        self.line.set_data(self.x,self.y)
       # self.legend(EMG Siganl)

        # 화면에 나타낼 x축 범위 업데이트
        if self.x[-1] >= self.xstart + self.xmax :
            #전체 x값중 반을 화면 옆으로 밀기
            self.xstart = self.xstart + self.xmax/2
            self.ax.set_xlim(self.xstart,self.xstart + self.xmax)

            self.ax.figure.canvas.draw()

        return (self.line, )

class Scope1(object):
    
    # 초기 설정
    # X-axis setting
    def __init__(self,
                 ax,fn,
                 xmax=5,ymax =100,
                 xstart=0, ystart=0,
                 title='Real Time Envelope Signal',xlabel='Time(sec)',ylabel='Envelope(V)'):
        
        self.xmax = xmax #x축 길이
        self.xstart = xstart #x축 시작점
        self.ymax = ymax #y축 길이
        self.ystart = ystart #y축 시작점

        # 그래프 설정
        self.ax = ax 
        self.ax.set_xlim((self.xstart,self.xmax))
        self.ax.set_ylim((self.ystart,self.ymax))
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        self.x = [0] # x축 정보 
        self.y = [0] # y축 정보
        self.value = 0 # 축 값
        self.fn = fn
        self.line, = ax.plot([],[],color='r')

        self.ti = time.time() #현재시각
        print("초기화 완료")

    # 그래프 설정
    def update(self, i):
        # 시간차
        tempo = time.time()-self.ti
        self.ti = time.time() #시간 업데이트
        
        # 값 넣기
        self.value = self.fn()# y값 함수 불러오기
        self.y.append(self.value) #y값 넣기
        self.x.append(tempo + self.x[-1]) #x값 넣기
        self.line.set_data(self.x,self.y)
       # self.legend(EMG Siganl)

        # 화면에 나타낼 x축 범위 업데이트
        if self.x[-1] >= self.xstart + self.xmax :
            #전체 x값중 반을 화면 옆으로 밀기
            self.xstart = self.xstart + self.xmax/2
            self.ax.set_xlim(self.xstart,self.xstart + self.xmax)

            self.ax.figure.canvas.draw()

        return (self.line, )

fig = plt.figure() 
fig.subplots_adjust(hspace=0.7) #subplot 사이 간격 조절

ax = plt.subplot(2,1,1)
plt.grid()
ax1 = plt.subplot(2,1,2)
plt.grid()

# y축에 표현할 값을 반환해야하고 scope 객체 선언 전 선언해야함.
def insert():
    value = ms.readAnalog(mcp_emg, EMG)
    return value

def insert_env():
    value = ms.readAnalog(mcp_env, Envelope)
    return value
    
# 객체 생성
# y-axis setting
scope_emg = Scope(ax,insert, ystart = 0.0, ymax = 3.0)
scope_env = Scope1(ax1,insert_env, ystart = 0.0, ymax = 3.0)

# update 매소드 호출

ani =animation.FuncAnimation(fig, scope_emg.update,interval=0.01,blit=1)
ani_2 = animation.FuncAnimation(fig, scope_env.update,interval=0.01,blit=1)
plt.show()


