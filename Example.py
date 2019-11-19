from IM.TCPIP import IM

myIM = IM() # create an instance of IM with default TCPIP port

myIM.getStatus() # return Ready or Busy

## Go to XYZ
myIM.gotoXY(X=10.123, Y=25.567 ) # X and Y in mm
myIM.gotoZ(Z=130.5) # Z in um

## Get XYZ
Xmm,Ymm,Zum = myIM.getXaxis(), myIM.getYaxis(), myIM.getZaxis()

## At the end
myIM.closeSocket() # To free the TCPIP port