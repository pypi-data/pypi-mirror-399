# -*- coding: utf-8 -*-
"""
Created on Fri Dec 26 07:06:40 2025

@author: ACER
"""

def miangin(numbers:list):
    #محاسبه میانگین
    
    count = 0
    sm = 0
    for adad in numbers:
        count += 1
        sm += adad
    return sm / count

def variance(numbers:list):  
#محاسبه واریانس 
    
    sm = 0
    count = 0
    for adad in numbers:
        sm += adad
        count += 1 
    mean = sm / count
    sm_of_squares = 0
    for adad in numbers :
       
        sm_of_squares += (adad-mean)**2
  #واریانس برابر است با میانگین مربعات فاصله ها از میانگین
    return sm_of_squares / count

def enheraf_meyar(numbers:list):
    # محاسبه انحراف معیار 
    sm = 0
    count = 0
    for adad in numbers:
        sm += adad
        count += 1   
    mean = sm / count
    sm_of_squares = 0
    for adad in numbers:
        sm_of_squares += (adad-mean)**2
    variance = sm_of_squares / count
   #انحراف معیار برابر است با جذر واریانس
    return variance ** 0.5

def data_range(numbers:list):
    #محاسبه دامنه اعداد
    minimom = numbers[0]
    maximom = numbers[0]
    #دامنه برابر است با بیشترین مقدار منهای کمترین
    for adad in numbers:
        if adad < minimom:
            minimom = adad
        if adad > maximom:
            maximom = adad
    return maximom - minimom

def median(numbers) :
    # محاسبه مد
    sorted_nums = sorted(numbers)
    count = 0
    for _ in sorted_nums:
        count += 1
    mid = count // 2

    # اگر تعداد فرد باشه برابر است با عنصر وسط
    if count % 2 == 1:
        return sorted_nums[mid]
    else:
        # اگر تعداد زوج باشه برابر است با میانگین دو عنصر وسط
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2


