'''
从临床数据库gdc_manifest.Clinical_Supplement.tsv中患者标示码对应读取文件名
筛选临床表现stage，T分类和存活时长数据完备的样本，保存至Clinical_Supplement_jh.csv文件中
'''
import csv   
from xml.etree import ElementTree as ET

csvfile = file('/Users/jiahao/Desktop/jh/gdc_manifest.Clinical_Supplement.tsv','rb')
reader = csv.reader(csvfile)
data = []
count1_stage = 0 	#stage正样本数
count2_stage = 0	#stage副样本数
count3_stage = 0	#stage未知样本数

count1_time = 0		#存活时长正样本数
count2_time = 0		#存活时长负样本数
count3_time = 0     #存活时长未知样本数

count1_T = 0	#T分类正样本数
count2_T = 0	#T分类负样本数
count3_T = 0	#T分类未知样本数
for row in reader:
	temp1  = ['/Users/jiahao/Desktop/jh/Clinical Supplement/', row[0], '/', row[1]]
	path = ''
	path = ''.join(temp1)
	tree = ET.parse(path)
	root = tree.getroot()
	admin = root.find('{http://tcga.nci/bcr/xml/administration/2.7}admin')
	patient = root.find('{http://tcga.nci/bcr/xml/clinical/coad/2.7}patient')
	follow_ups = patient.find('{http://tcga.nci/bcr/xml/clinical/coad/2.7}follow_ups').find('{http://tcga.nci/bcr/xml/clinical/coad/followup/2.7/1.0}follow_up')	
	if follow_ups == None:
		continue
	bcr_patient_barcode = patient.find('{http://tcga.nci/bcr/xml/shared/2.7}bcr_patient_barcode').text
	stage_event = patient.find('{http://tcga.nci/bcr/xml/clinical/shared/stage/2.7}stage_event')
	pathologic_categories = stage_event.find('{http://tcga.nci/bcr/xml/clinical/shared/stage/2.7}tnm_categories').find('{http://tcga.nci/bcr/xml/clinical/shared/stage/2.7}pathologic_categories')
	##stage#
	ajcc_pathologic_tumor_stage = stage_event.find('{http://tcga.nci/bcr/xml/clinical/shared/stage/2.7}pathologic_stage').text
	l1 = ['Stage I','Stage IA','Stage II','Stage IIA','Stage IIB','Stage IIC'] #stage正样本范围
	l2 = ['Stage III','Stage IIIA','Stage IIIB','Stage IIIC','Stage IV','Stage IVA','Stage IVB'] #stage负样本范围
	if ajcc_pathologic_tumor_stage in l1:  #stage样本情况统计
		tumor_stage_output = 1
		count1_stage = count1_stage + 1
	elif ajcc_pathologic_tumor_stage in l2:
		tumor_stage_output = -1
		count2_stage = count2_stage + 1
	else:
		tumor_stage_output = 0
		count3_stage = count3_stage + 1
	##stage_T
	ajcc_tumor_pathologic_T = pathologic_categories.find('{http://tcga.nci/bcr/xml/clinical/shared/stage/2.7}pathologic_T').text
	if ajcc_tumor_pathologic_T[1] == '1' or ajcc_tumor_pathologic_T[1] == '2': #T分类样本情况统计
		tumor_T_output = 1
		count1_T = count1_T + 1
	elif ajcc_tumor_pathologic_T[1] == '3' or ajcc_tumor_pathologic_T[1] == '4':
		tumor_T_output = -1
		count2_T = count2_T + 1
	else:
		tumor_T_output = 0
		count3_T = count3_T + 1

	##live time#
	year_of_initial_pathologic_diagnosis = patient.find('{http://tcga.nci/bcr/xml/clinical/shared/2.7}year_of_initial_pathologic_diagnosis').text
	follow_up_vital_status = follow_ups.find('{http://tcga.nci/bcr/xml/clinical/shared/2.7}vital_status').text
	follow_up_days_to_death = follow_ups.find('{http://tcga.nci/bcr/xml/clinical/shared/2.7}days_to_death').text
	follow_up_form_completion_year = follow_ups.find('{http://tcga.nci/bcr/xml/clinical/shared/2.7}year_of_form_completion').text

	if follow_up_vital_status == 'Alive':  #存活时长样本情况统计
		if (float(follow_up_form_completion_year)-float(year_of_initial_pathologic_diagnosis)>=3):
			tumor_time_output = 1
			count1_time = count1_time+1
		else:
			tumor_time_output = -1
			count2_time = count2_time+1
	elif follow_up_vital_status == 'Dead':
		if follow_up_days_to_death == None:
			follow_up_days_to_death = 0
		if (float(follow_up_form_completion_year)-float(year_of_initial_pathologic_diagnosis)-float(follow_up_days_to_death)/365>=3):
			tumor_time_output = 1
			count1_time = count1_time +1
		else:
			tumor_time_output = -1
			count2_time = count2_time+1
	else:
		tumor_time_output = 0
		count3_time = count3_time+1
    

	temp2 = [bcr_patient_barcode,ajcc_pathologic_tumor_stage,tumor_stage_output,ajcc_tumor_pathologic_T,tumor__output,year_of_initial_pathologic_diagnosis,follow_up_vital_status,follow_up_days_to_death,follow_up_form_completion_year,tumor_time_output]
	data.append(temp2)

csvfile.close()
csvfile = file('/Users/jiahao/Desktop/jh/Clinical_Supplement_jh.csv','wb')
writer = csv.writer(csvfile)
writer.writerow(['bcr_patient_barcode','ajcc_pathologic_tumor_stage','tumor_stage_output','ajcc_tumor_pathologic_T','tumor_T_output','year_of_initial_pathologic_diagnosis','follow_up_vital_status','follow_up_days_to_death','follow_up_form_completion_year','tumor_time_output'])
writer.writerows(data)
csvfile.close()
print count1_stage,count2_stage,count3_stage
print count1_T,count2_T,count3_T
print count1_time,count2_time,count3_time

'''
根据患者条形码，对比Clinical_Supplement_jh患者临床数据和relation.csv患者组学数据集。
将临床数据和组学数据齐全的患者以下数据：
    1.条形码（bcr_patient_barcode）
    2.对应的组学数据文件名（甲基化、CNV、miRNA和基因表达）
    3.临床分类结果（stage、T分类、存活时长）
保存在Cli_relation1.csv文件中
'''
csvfile = file('/Users/jiahao/Desktop/jh/Clinical_Supplement_jh.csv','rb')
reader = csv.reader(csvfile)
data = []
count_cli =0
count_rela =0
l = [None,'',0,'0']
count1_stage = 0
count2_stage = 0

count1_time = 0
count2_time = 0

count1_T = 0
count2_T = 0

for row in reader:
	if row[0] == 'bcr_patient_barcode':
		continue
	csvfile2 = file('/Users/jiahao/Desktop/jh/relation.csv','rb')
	reader2 = csv.reader(csvfile2)
	for row2 in reader2:
		if row2[0] == 'bcr_patient_barcode':
			continue
		if (row[2] in l)or(row[4] in l)or(row[9] in l)or(row2[1] in l)or(row2[6] in l)or(row2[22] in l)or(row2[28] in l):  #判断临床表现和组学数据是否齐全
			continue 
		if (row2[0] == row[0]):
			if row[2] == '-1':
				count1_stage = count1_stage +1
			elif row[2] =='1':
				count2_stage = count2_stage +1

			if row[4] == '-1':
				count1_T = count1_T +1
			elif row[4] =='1':
				count2_T = count2_T +1

			if row[9] == '-1':
				count1_time = count1_time +1
			elif row[9] =='1':
				count2_time = count2_time +1
			data.append([row2[0],row2[1],row2[6],row2[22],row2[28],row[2],row[4],row[9]])
			count_rela = count_rela+1
			break
	csvfile2.close()
	count_cli = count_cli + 1
	
csvfile.close()
csvfile = file('/Users/jiahao/Desktop/jh/Cli_relation.csv','wb')
writer = csv.writer(csvfile)
writer.writerow(['bcr_patient_barcode','DNA_Methylation','Copy_Number_Variation','miRNA_Expression_Quantification','Gene_Expression_Quantification_counts','stage_outcome','T_outcome','time_outcome'])
writer.writerows(data)
csvfile.close()
print count_cli,count_rela
print count1_stage,count2_stage
print count1_T, count2_T
print count1_time,count2_time
