# -*- coding: utf-8 -*-
import cv2 as cv
from reportlab.pdfgen import canvas
import numpy as np
import pytesseract

#Variaveis gerais

frame_selecionado = None
x_select_0 = 25
y_select_0 = 25
x_select_1 = 600
y_select_1 = 450


list_rect_selecionados = []
list_infos = ['Foto','Nome','Posicao','Matricula','Lotacao']
list_OCR_texto = []

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

def desenha_limites(frame):
    cv.rectangle(frame,
        (x_select_0,y_select_0),
        (x_select_1,y_select_1),
        (255,255,255),
        2,
        cv.LINE_AA
        )
    cv.putText(frame,
            '[q - sair] [c - continuar]',
            (0,470),
            cv.FONT_HERSHEY_DUPLEX,
            0.5,
            (255,255,255),
            1)
    return frame

def captura_documento():
    cam = cv.VideoCapture(1,cv.CAP_DSHOW)
    while True:
        if cam.isOpened():
            isCap,frame = cam.read()
            frame = desenha_limites(frame)
            if isCap:
                cv.imshow('Selecionar_Documento',frame)
                key = cv.waitKey(50)
                
                if key == ord('q'):
                    cv.destroyAllWindows()
                    cam.release()
                    return key
                if key == ord('c'):
                    cv.destroyAllWindows()
                    cam.release()
                    global frame_selecionado
                    frame_selecionado = frame[y_select_0:y_select_1,x_select_0:x_select_1]
                    return key


def avalia_documento():
    frame_complemento = np.full((50,575,3),(0,0,0),dtype = np.uint8)
    cv.putText(frame_complemento,
                'Certifique se,de que os dados do documento estao',
                (0,10),
                cv.FONT_HERSHEY_DUPLEX,
                0.4,
                (255,255,255),
                1)
    cv.putText(frame_complemento,
                'visiveis antes de seguir.',
                (0,25),
                cv.FONT_HERSHEY_DUPLEX,
                0.4,
                (255,255,255),
                1)
    cv.putText(frame_complemento,
                '[q - Tentar Novamente] [c - Tudo certo, continuar]',
                (0,45),
                cv.FONT_HERSHEY_DUPLEX,
                0.4,
                (255,255,255),
                1)
    resultado = cv.vconcat([frame_selecionado,frame_complemento])
    cv.imshow('Amostra',resultado)
    key = cv.waitKey()
    cv.destroyAllWindows()
    return key

def confirma_selecao():
    global frame_selecionado
    global list_rect_selecionados
    
    frame_complemento = np.full((50,575,3),(0,0,0),dtype = np.uint8)
    cv.putText(frame_complemento,
                'Os dados estao corretos? [s/n]',
                (0,10),
                cv.FONT_HERSHEY_DUPLEX,
                0.4,
                (255,255,255),
                1)
    
    frame_white = np.full((450,575,3),(255,255,255),dtype = np.uint8)
         
    for roi in list_rect_selecionados:
   
       x0,y0,w,h = roi
       
       frame_white[y0:(y0+h),x0:(x0+w)] = frame_selecionado[y0:(y0+h),x0:(x0+w)]
      
    resultado = cv.vconcat([frame_white,frame_complemento])
    cv.imshow('Validar',resultado)
    key = cv.waitKey()
    if key == ord('s'):
        cv.destroyAllWindows()
        return key
    else:
        cv.destroyAllWindows()
        seleciona_segmentos()
        
    

def seleciona_segmentos():
    global frame_selecionado
    global list_rect_selecionados
    global list_infos
    
    for docs in list_infos:
        rect = cv.selectROI('Selecione_'+docs,frame_selecionado,False)
        
        if rect and np.sum(rect) > 0:
            list_rect_selecionados.append(rect)
        cv.destroyAllWindows()
    return confirma_selecao()
        

def realiza_ocr():
    global list_rect_selecionados
    global frame_selecionado
    global list_OCR_texto
    
    x0,y0,w,h = list_rect_selecionados[0]
    
    list_OCR_texto.append(frame_selecionado[y0:(y0+h),x0:(x0+w)])
    
    for roi in list_rect_selecionados[1:]:
   
       x0,y0,w,h = roi
       
       imagem_leitura = cv.cvtColor(frame_selecionado[y0:(y0+h),x0:(x0+w)],cv.COLOR_BGR2RGB)
       imagem_leitura = cv.cvtColor(imagem_leitura,cv.COLOR_RGB2GRAY)
       
       
       teste = cv.threshold(imagem_leitura,0,127,cv.THRESH_BINARY | cv.THRESH_OTSU)[1]
        
       teste = cv.medianBlur(teste,1)
       list_OCR_texto.append(pytesseract.image_to_string(teste,lang='eng'))
       print(pytesseract.image_to_string(teste,lang='eng'))
       # cv.imshow('OCR',teste)
       # cv.waitKey()
       # cv.destroyAllWindows()
    
    
def gera_pdf():
    
    global list_OCR_texto
    
    
    pdf = canvas.Canvas('doc.pdf')
    
    
    pdf.setTitle('Documento OCR')
    
    pdf.drawString(50,800,'Colaborador:')
    
    cv.imwrite('foto.png',list_OCR_texto[0])
    pdf.drawImage('foto.png',50,700,80,80)
    
    pdf.drawString(50,650,'Informações:')
    
    pos = 650
    
    for info in list_OCR_texto[1:]:
        pos-=20
        pdf.drawString(50,pos,info)
        
    pdf.save()
         
while True:
    
    key = captura_documento()
   
    if key == ord('q'):
        break
    elif key == ord('c'):
       
        key = avalia_documento() 
        if key == ord('q'):
            break
        else:
           seleciona_segmentos()
           realiza_ocr()
           gera_pdf()
           
    
    
    