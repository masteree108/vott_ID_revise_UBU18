import os
import tkinter as Tk
import tkinter.font as font
from tkinter import messagebox
import matplotlib
import matplotlib.pyplot as plt
#import matplotlib.image as mpimg # mpimg 用于读取图片
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import filedialog       #獲取文件全路徑
import log as PYM
import threading
import time
import queue
import numpy as np
from multiprocessing import shared_memory
from PIL import Image
from skimage import transform,data
import platform
from pathlib import Path

class tool_display():

#private
    __log_name = '< class tool display>'
    __root = Tk.Tk()
    __canvas = 0
    __system_file_path = './system/'
    __file_process_path = './.system/file_process/'
    __set_font = font.Font(name='TkCaptionFont', exists=True)
    #__share_array_name = 'image'
    __logo_path = "default_img/logo_combine.jpg"
    __shm_size = 100
    __page_counter = 0
    __next_amount_of_people = 0
    __next_amp_12_unit = []
    __combine_table_path = "./.system/combine"
    __process_working = False
    __interval = 1
    __amount_of_cur_people = 0
    __amount_of_next_people = 0

    def __init_buttons(self):
        # quit button
        quit_btn = Tk.Button(master = self.__root, text = 'Quit', command = self.system_quit)
        quit_btn['font'] = self.__set_font
        #quit_btn.pack(side = Tk.BOTTOM)
        quit_btn.pack(side = Tk.RIGHT)
        
        # open image button, this is for testing function
        open_img_btn = Tk.Button(master = self.__root, text='選擇1張圖片', command = self.open_image)  #設置按鈕，並給它openpicture命令
        open_img_btn['font'] = self.__set_font
        # below comment out that means hided this button
        #open_img_btn.pack(side = Tk.RIGHT)
        
        # get *.json data path button
        # 設置按鈕，並給它openpicture 命令
        get_json_data_path_btn = Tk.Button(master = self.__root, text='選擇json file來源資料夾', command = self.find_json_file_path)
        get_json_data_path_btn['font'] = self.__set_font
        get_json_data_path_btn.pack(side = Tk.RIGHT)
        
        # go back to previous step
        go_back_to_prv_step_btn = Tk.Button(master = self.__root, text='還原上一動', command = self.go_back_to_previous_step)
        go_back_to_prv_step_btn['font'] = self.__set_font
        go_back_to_prv_step_btn.pack(side = Tk.RIGHT)

        # revise button
        self.__revise_btn = Tk.Button(master = self.__root, text='執行修正', command = self.run_feature_match)  #設置按鈕，並給它修正命令
        self.__revise_btn['font'] = self.__set_font
        self.__revise_btn.pack(side = Tk.RIGHT)

        # reviseOK button
        self.__reviseOK_btn = Tk.Button(master = self.__root, text='修正完成', command = self.send_revise_id_to_feature_match_process)
        self.__reviseOK_btn['font'] = 12
        self.__reviseOK_btn.place(x = 1700, y = 900)

        # next page button
        self.__next_page_btn = Tk.Button(master = self.__root, text='下一頁', command = self.display_next_page)
        self.__next_page_btn['font'] = 12
        self.__next_page_btn.place(x = 1600, y = 900)

        # previous page button
        self.__prv_page_btn = Tk.Button(master = self.__root, text='上一頁', command = self.display_cur_page)
        self.__prv_page_btn['font'] = 12
        self.__prv_page_btn.place(x = 1500, y = 900)

        #hide below button
        self.__visible_reviseOk_btn(False)
        self.__visible_next_page_btn(False)
        self.__visible_prv_page_btn(False)

    def __check_file_not_finished(self):
        if os.path.isdir(self.__file_process_path) != 0:
            return self.askokcancel_msg_on_toast("注意", "還有尚未完成的file,是否要重新開始？")
        else:
            return True

    def __check_file_process_folder_has_any_files(self):
        if os.path.isdir(self.__file_process_path) != 0:
            return self.askokcancel_msg_on_toast("注意", "還有尚未完成的file,是否要重新開始？")
        else:
            return True

    def __ask_user_to_make_sure_run_go_back_(self):
        return self.askokcancel_msg_on_toast("注意", "是否要執行此動?(執行此動後此動完成的json會被刪除)")

    def __update_canvas(self, new_img):
        self.ax.clear()
        plt.axis('off')
        plt.imshow(new_img)
        self.__canvas.draw()

    def __init_shared_memory(self, next_round):
        shm_list = []
        shm_list.append(0)  #amount of images (=12 be an unit)
        shm_list.append(1)  #amount of images (=12 state)
        for i in range(2,self.__shm_size):
            shm_list.append('null')
        if next_round == 0:
            self.shm_id = shared_memory.ShareableList(shm_list)

    def __visible_reviseOk_btn(self, sw):
        if sw == True:
            self.__reviseOK_btn.place(x = 1700, y = 900)
        else:
            self.__reviseOK_btn.place_forget()

    def __visible_next_page_btn(self, sw):
        if sw == True:
            self.__next_page_btn.place(x = 1600, y = 900)
        else:
            self.__next_page_btn.place_forget()

    def __visible_prv_page_btn(self, sw):
        if sw == True:
            self.__prv_page_btn.place(x = 1500, y = 900)
        else:
            self.__prv_page_btn.place_forget()

    def __visible_revise_btn(self, sw):
        if sw == True:
            self.__revise_btn.pack(side = Tk.RIGHT)
        else:
            #self.__revise_btn.place_forget()
            self.__revise_btn.grid(column=0, row=0, padx=10, pady=10)


    def __show_entry_boxes(self, index):
        x_axis_ct = 0
        if index > 0:
            range1  = index * 12
            range2 = self.__next_amp_12_unit[index] + 12
        else:
            # into this section because index = 0
            range1  = 0
            range2 = self.__next_amp_12_unit[index]

        y_axis = 50
        #if self.__next_amount_of_people - range2 < 0:
            #y_axis = 180
        #else:
            #y_axis = 50

        # clean all
        self.__hide_all_entry_boxes()

        #show this page
        for i in range(range1, range2):
            if self.__entry_list[i][1] != 'null':
                if i % 4 == 0:
                    y_axis = y_axis + 190
                    if y_axis > 500:
                        y_axis = y_axis-30
                    x_axis_ct = 0
                x_axis_ct = x_axis_ct + 1
                self.__entry_list[i][0].place(width=80,height=30,x=820+x_axis_ct*160, y=y_axis)
            else:
                break

    def __hide_all_entry_boxes(self):
        # clean all
        for i,entry in enumerate(self.__entry_list):
            entry[0].place_forget()

        
    def __load_next_frame_img_and_update_screen(self, index):
        #img = mpimg.imread('next_no_ids_img_table_' + str(index) + '.png')
        img = Image.open(self.__combine_table_path + str(index) + '.png')
        
        self.pym.PY_LOG(False, 'D', self.__log_name, 'image_shape: %s' % str(img.size))
        #people = (index + 1) * 12
        #if self.__next_amount_of_people - people < 0:
            #img = img.resize((1000,800))
        #self.pym.PY_LOG(False, 'D', self.__log_name, 'image_shape: %s' % str(img.size))
        self.__update_canvas(img)

    def __check_interval_val_and_return_val(self):
        val = int(self.entry_check_interval.get())
        if val>5 or val<1:
            return False,0
        else:
            return True,val

    def __hide_specify_btns_and_init_canvas(self):
        self.__visible_reviseOk_btn(False)
        self.__visible_next_page_btn(False)
        self.__visible_prv_page_btn(False)
        self.__hide_all_entry_boxes()
        self.__update_canvas(self.__image_logo)

    def __delete_all_entry_boxes(self):
        # delete all
        for i,entry in enumerate(self.__entry_list):
            del entry
        self.__entry_list = []
        self.pym.PY_LOG(False, 'D', self.__log_name, '---------------delete all entry boxes----------------')

    def __clear_shm_id(self):
        self.pym.PY_LOG(False, 'D', self.__log_name, '---------------clear shm id----------------')
        for i in range(len(self.shm_id)):
            self.shm_id[i] = 'null'

#public
    def __init__(self, td_que, fm_process_que):
        
        self.__amount_of_cur_people = 0
        self.__amount_of_next_people = 0

        self.__init_shared_memory(next_round=0)
        
        self.__process_working = False

        self.__interval = 1

        self.__set_font.config(family='courier new', size=10)
        self.td_queue = td_que
        self.fm_process_queue = fm_process_que
        self.pym = PYM.LOG(True)
        matplotlib.use('TkAgg')
        
        os_name = self.which_os()
        self.pym.PY_LOG(False, 'D', self.__log_name, 'OS:' + '%s' % os_name)
        if os_name == 'Linux':
            #規定窗口大小
            #self.__root.geometry('2000x2000')
            #self.__root.resizable(width = False, height = False)   # 固定长宽不可拉伸
            self.__root.attributes('-zoomed', True)
        elif os_name == 'Windows':
            #self.__root.resizable(width = False, height = False)   # 固定长宽不可拉伸
            self.__root.state('zoomed')
            #self.__root.state('normal')

        self.__root.title("統一VoTT json file 內的人物ID")
        self.figure, self.ax = plt.subplots(1, 1, figsize=(16, 8))
        self.pym.PY_LOG(False, 'D', self.__log_name, 'self.figure:' + '%s' % self.figure)
        self.__image_logo = Image.open(self.__logo_path)
        plt.imshow(self.__image_logo)
        plt.axis('off')

        #放置標籤
        self.label1 = Tk.Label(self.__root,text = '下方會顯示比對的ID人物表', image = None, font = self.__set_font)   #創建一個標籤
        self.label2 = Tk.Label(self.__root,text = '處理狀態', image = None, font = self.__set_font)   #創建一個標籤
        self.label2 = Tk.Label(self.__root,text = 'system state', image = None, font = self.__set_font)   #創建一個標籤
        self.label1.pack()
        self.label2.pack()

        #把繪製的圖形顯示到tkinter視窗上
        self.canvas_draw()

        #把matplotlib繪製圖形的導航工具欄顯示到tkinter視窗上
        toolbar = NavigationToolbar2TkAgg(self.__canvas, self.__root)
        toolbar.update()
        self.__canvas._tkcanvas.pack(side = Tk.TOP, fill = Tk.BOTH, expand = 1)

        self.__init_buttons()
        '''
        self.WKU_queue = queue.Queue()
        self.TDU_queue = queue.Queue()
        self.wk = Worker(self.td_queue, self.WKU_queue, self.TDU_queue)
        self.wk.start()
        '''
        self.__root.protocol("WM_DELETE_WINDOW", self.system_quit)

        # entry box for check sec settings
        # max=5 , min=1
        self.check_interval_label = Tk.Label(self.__root, font=self.__set_font, text="check interval(sec):")
        self.check_interval_label.place(width=400,height=30,x=10, y=900)
        self.entry_check_interval = Tk.Entry(self.__root, bd=2, font=self.__set_font)
        #self.entry_check_interval.pack(side = Tk.LEFT)
        self.entry_check_interval.place(width=50,height=30,x=420, y=900)
        #self.entry_check_interval.pack(side = Tk.LEFT)
        self.entry_check_interval.insert(0,"1")


    def __del__(self):               
        #deconstructor
        self.shut_down_log("over")
        '''
        try:
            sa.delete(self.__share_array_name)
        except:
            self.pym.PY_LOG(False, 'D', self.__log_name, 'share_array:%s has been deleted' % self.__share_array_name)
        '''

    def canvas_draw(self):
        self.__canvas = FigureCanvasTkAgg(self.figure, master = self.__root)
        self.__canvas.draw()
        self.__canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand = 1)

    def open_image(self):
        file_name = filedialog.askopenfilename()     #獲取文件全路徑
        self.__open_image_path = file_name
        if os.path.isfile(file_name):
            self.pym.PY_LOG(False, 'D', self.__log_name, 'open image path:' + '%s' % file_name)
            self.label2.config(text = 'image path:' + file_name )
            #image = mpimg.imread(file_name)
            image = Image.open(file_name)
            #image = image.resize((1000,800))
            self.__update_canvas(image)
        else:
            self.label2.config(text = 'image path is not existed!!' )  


    def go_back_to_previous_step(self):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'go_back_to_previous_step')

        if self.__process_working == False:
            self.fm_process_queue.put("ask_prv_action:")
            msg = self.td_queue.get()
            if msg == "no_prv_step":
                self.pym.PY_LOG(False, 'D', self.__log_name, 'no previous action')
                self.show_error_msg_on_toast("錯誤", "沒有上一動！")
            else:
                if self.__ask_user_to_make_sure_run_go_back_():
                    self.fm_process_queue.put("run_prv_action:")

                    msg = self.td_queue.get()
                    if msg == 'prv_finished:':
                        self.pym.PY_LOG(False, 'D', self.__log_name, 'go back to previous step finished')
                        self.show_info_msg_on_toast("提醒", "已完成回復至上一動")
        else:
            self.show_error_msg_on_toast("錯誤", "請先完成此次修正")
            

    def find_json_file_path(self):
        if self.__process_working == True:
            self.show_error_msg_on_toast("錯誤", "請先執行 修正完成")
            return

        if self.__check_file_not_finished() == True:
            #start or restart this process
            file_path = filedialog.askdirectory()     #獲取*.json檔案資料夾路徑
            if os.path.isdir(file_path):
                self.pym.PY_LOG(False, 'D', self.__log_name, 'json file path:' + '%s' % file_path)
                self.fm_process_queue.put("json_file_path:" + str(file_path)); 
                self.label2.config(text = 'json file path:' + file_path )
                #shutil.rmtree(self.__system_file_path)

            else:
                self.pym.PY_LOG(False, 'D', self.__log_name, 'json file path:' + '%s' % file_path + 'is not existed!!')
                self.label2.config(text = 'json file path is not existed!!' )  
        else:
            self.show_error_msg_on_toast("錯誤", "請繼續執行 執行修正 按鈕")
            
    def run_feature_match(self):
        if self.__process_working == True:
            self.show_error_msg_on_toast("錯誤", "請先執行 執行修正完成")
            self.pym.PY_LOG(False, 'D', self.__log_name, '!!!!process still wroking, so disabled revise bth functionailty!!!!')
            return

        interval_ok, self.__interval = self.__check_interval_val_and_return_val()
        if interval_ok == False:
            self.show_error_msg_on_toast("錯誤", "check interval max=5,min=1")
            self.pym.PY_LOG(False, 'D', self.__log_name, 'check interval max=5,min=1')
            return

        self.__process_working = True
        self.pym.PY_LOG(False, 'D', self.__log_name, '========ready to send check_file_exist_and_match into queue=========')
        self.fm_process_queue.put("check_file_exist_and_match:" + str(self.__interval))
        msg = self.td_queue.get()

        if msg == 'file_exist:':
            self.label2.config(text = '等待ID比對中...畫面不會更新直到比對完成（請勿移動畫面！！)')
            self.show_info_msg_on_toast("提醒", "比對中 請等待比對完成 請勿移動視窗,按下 ok 後繼續執行")
            
            #self.show_info_msg_on_toast("提醒", "畫面為判斷後之ID,請與id_image_table視窗比對手對校正,完成請按下確認按鈕")
            # waiting for feature process is ok
            uint = 12
            msg = self.td_queue.get()
            if msg == 'match_ok:':
                self.label2.config(text = 'ID比對完成')

                msg = self.td_queue.get()
                if msg[:23]== 'show_combine_img_table:':
                    cur_people_index = msg.find(':') + 1
                    next_people_index = msg.find(';')
                    self.__amount_of_cur_people = int(msg[cur_people_index:next_people_index])
                    self.__amount_of_next_people = int(msg[next_people_index+1:])
                    self.pym.PY_LOG(False, 'D', self.__log_name, 'amount_of_cur_people:%d' % self.__amount_of_cur_people)
                    self.pym.PY_LOG(False, 'D', self.__log_name, 'amount_of_next_people:%d' % self.__amount_of_next_people)
                    '''
                    with open('cur_ids_img_table', 'rb') as f:
                        str_encode = f.read()
                    decode_img = np.asarray(bytearray(str_encode), dtype='uint8')
                    decode_img = cv2.imdecode(decode_img, cv2.IMREAD_COLOR)
                    self.__update_canvas(decode_img)
                    '''
                    
                    self.__entry_list = []
                    ct = 0
                    ct_amt = 0
                    size =  self.shm_id[0]
                    state =  self.shm_id[1]
                    for i in range(2,len(self.shm_id)):
                        if self.shm_id[i] != 'null':
                            ct_amt +=1
                            self.__next_amount_of_people +=1
                            self.__entry_list.append([])
                            self.__entry_list[ct].append(Tk.Entry(font=8))
                            self.__entry_list[ct].append(self.shm_id[i])
                            ct = ct + 1
                            self.pym.PY_LOG(False, 'D', self.__log_name, 'get new id:%s' % self.shm_id[i])
                            if i % uint == 0 and i != 0:
                                self.__next_amp_12_unit.append(uint)
                        else:
                            break
                   
                    if (ct_amt - uint) > 0:
                        self.__next_amp_12_unit.append(ct_amt - uint)
                    else:
                        self.__next_amp_12_unit.append(ct_amt)
                        
                    self.pym.PY_LOG(False, 'D', self.__log_name, 'amp_12_unit:%s' % str(self.__next_amp_12_unit))

                    # fill id data into every entry box
                    for i,entry in enumerate(self.__entry_list):
                        entry[0].insert(0, entry[1])

                    self.__load_next_frame_img_and_update_screen(index=0)
                    self.__show_entry_boxes(index=0)

                    if self.__next_amount_of_people > 12:
                        self.__visible_next_page_btn(True)
                        self.__visible_prv_page_btn(True)

                    self.__visible_reviseOk_btn(True)

                    self.show_info_msg_on_toast("提醒", "畫面為判斷後之ID,請與id_image_table視窗比對手對校正,完成請按下 修正完成 按鈕")

        elif msg == 'file_not_exist:':
            self.__process_working = False
            self.show_error_msg_on_toast("錯誤", "資料夾無任何.json file ,請按下 載入file 按鈕")
            self.pym.PY_LOG(False, 'D', self.__log_name, 'there no any json files in the folder')
        elif msg == 'file_too_few:':
            self.__process_working = False
            self.show_error_msg_on_toast("錯誤", "json file 數量太少無法執行(需大於fps X interval +1),剩餘.json file 請手動修正")
            self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of json files are too few')

    def display_main_loop(self):
        Tk.mainloop()

    def shut_down_log(self, msg):
        self.pym.PY_LOG(True, 'D', self.__log_name, msg)

    #按鈕單擊事件處理函式
    def system_quit(self):
        if self.__process_working == True:
            self.shm_id[1] = 0
            self.shut_down_log("over")
        #結束事件主迴圈，並銷燬應用程式視窗
        self.__root.quit()
        self.__root.destroy()
        self.shut_down_log("quit")
        self.shm_id.shm.close()
        self.shm_id.shm.unlink()

    def show_error_msg_on_toast(self, title, msg):
        messagebox.showerror(title, msg)

    def show_info_msg_on_toast(self, title, msg):
        messagebox.showinfo(title, msg)

    def show_warning_msg_on_toast(self, title, msg):
        messagebox.showwarning(title, msg)

    def askokcancel_msg_on_toast(self, title, msg):
        return messagebox.askokcancel(title, msg)

    #定義並繫結鍵盤事件處理函式
    def on_key_event(self, event):
        print('you pressed %s'% event.key)
        key_press_handler(event, canvas, toolbar)
        canvas.mpl_connect('key_press_event', on_key_event)

    def get_shm_name_and_size(self):
        return self.shm_id.shm.name, self.__shm_size
    
    def display_next_page(self):
        # update screen
        size = len(self.__next_amp_12_unit)
        if (self.__page_counter + 1) < size:
            self.__page_counter = self.__page_counter + 1
            index = self.__page_counter
            self.__load_next_frame_img_and_update_screen(index)
            self.__show_entry_boxes(index)

    def display_cur_page(self):
        # update screen
        if (self.__page_counter - 1) >= 0:
            self.__page_counter = self.__page_counter - 1
            index = self.__page_counter
            self.__load_next_frame_img_and_update_screen(index)
            self.__show_entry_boxes(index)

    def send_revise_id_to_feature_match_process(self):
        # get revise_id 
        revise_id_list = []
        id_ok = True

        if self.__amount_of_cur_people != self.__amount_of_next_people:
            self.show_warning_msg_on_toast("！！注意！！", "前後幀人數不相同,建議回vott確認是否漏框並進行追蹤,再重回此動作!!")
            self.show_warning_msg_on_toast("！！注意！！", "前幀人數:%s" % str(self.__amount_of_cur_people) + ", 後幀人數:%s" % str(self.__amount_of_next_people))

        for i,entry in enumerate(self.__entry_list):
            revise_id = entry[0].get()
            find_index = np.array(revise_id_list)
            index = np.argwhere(find_index == revise_id)
            if len(index) >= 1:
                self.show_error_msg_on_toast("錯誤", "有重複之ID：%s, 請再檢查後再次按下按鈕" % revise_id)
                id_ok = False
                break                

            if revise_id[:3] != 'id_':
                self.show_error_msg_on_toast("錯誤", "尚有尚未修正之ID：%s,請修改後再次按下按鈕" % revise_id)
                id_ok = False
                break
            elif revise_id[:6] == 'id_???':
                self.show_error_msg_on_toast("錯誤", "尚有尚未修正之ID：%s,請修改後再次按下按鈕" % revise_id)
                id_ok = False
                break

            revise_id_list.append(revise_id)

        if id_ok:
            self.shm_id[0] = 0
            #state = self.shm_id[1]
            # fill those crrect data into shared list
            for i,id_val in enumerate(revise_id_list):
                self.pym.PY_LOG(False, 'D', self.__log_name, 'revise_id_by_user:%s' % i)
                self.shm_id[i+2] = id_val

            # modify shm_id[1](state) to 0 to notify feature_match_process id has been revised 
            self.shm_id[1] = 0

            # waiting for eature_match_process dealing with modify *.json context(id) ok 
            msg = self.td_queue.get()
            self.pym.PY_LOG(False, 'D', self.__log_name, 'receive mag about excel file:%s' % msg)
            if msg.find('_result.xlsx') != -1:
                self.pym.PY_LOG(False, 'D', self.__log_name, 'receive excel file name:%s' % msg)
                self.__reviseOK_btn.place_forget()
                self.show_info_msg_on_toast("id修正完成,之後請繼續按下 修正按鈕 執行其他幀檢查", "詳細請參考 " + msg) 
                self.__hide_specify_btns_and_init_canvas()
                self.reload_and_int_for_next_round()
                self.__process_working = False
                self.__delete_all_entry_boxes()
                self.__clear_shm_id()

    def reload_and_int_for_next_round(self):
        self.__init_shared_memory(next_round=1)
        self.__page_counter = 0
        self.__next_amount_of_people = 0
        self.__next_amp_12_unit = []
        self.__interval = 1
        self.__amount_of_cur_people = 0
        self.__amount_of_next_people = 0

    def which_os(self):
        os_name = platform.system()
        #if os_name == 'Linux':
        #elif os_name == 'Windows':
        return os_name

