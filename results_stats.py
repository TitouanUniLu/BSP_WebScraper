import pandas

#statsFile = open('')
sheet_names=['NASDAQ-2021','INNOVATION-2021' , 'FTSE-2021', 'GERMANY', 'FRANCE']  
for sheet in sheet_names:
    workbook = pandas.read_excel('ALL_BoD_SCRAPED_RESULTS.xlsx', sheet_name=sheet)     #change to ALL_INDICES-2021.xlsx when scraping with regex
    df = pandas.DataFrame(workbook)
    male_scraped = df['male']
    female_scraped = df['female']
    male_real = df['Board male']
    female_real = df['Board female']
    average_accuracy = []
    for i in range(0, len(male_scraped)):
        values = [male_real[i], male_scraped[i], female_real[i], female_scraped[i]]
        if 'error' not in values and 'wrong' not in values and 'missing' not in values:
            if male_scraped[i] != 0 and female_scraped[i] != 0:
                acc = (male_real[i]/male_scraped[i] + female_real[i]/female_scraped[i])/2 * 100
            elif male_scraped[i] == 0 and female_scraped[i] != 0:
                acc = (female_real[i]/female_scraped[i])/2 * 100
            elif female_scraped[i] == 0 and male_scraped[i] != 0:
                acc = (male_real[i]/male_scraped[i])/2 * 100
            else:
                acc = 0
        if acc > 100:
            acc = 100/acc    
        average_accuracy.append(acc)
    print(sheet, sum(average_accuracy)/len(average_accuracy))