import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import datetime
import urllib

def download_data(province_id, year1=1981, year2=2024):
    data_folder = 'data'
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    else:
        existing_files = [f for f in os.listdir(data_folder) if f.startswith(f'vhi_id__{province_id}__')]
        if existing_files:
            return

    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_id}&year1={year1}&year2={year2}&type=Mean"
    vhi_url = urllib.request.urlopen(url)

    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f'vhi_id__{province_id}__{current_datetime}.csv'
    file_path = os.path.join(data_folder, filename)
    
    with open(file_path, 'wb') as out:
        out.write(vhi_url.read())

for i in range(1, 28):
    download_data(i)

def create_data_frame(folder_path):
    csv_files = glob.glob(folder_path + "/*.csv")
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    frames = []
    
    for file in csv_files:
        region_id = int(file.split('__')[1])
        df = pd.read_csv(file, header=1, names=headers)
        df.at[0, 'Year'] = df.at[0, 'Year'][9:]
        df = df.drop(df.index[-1])
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df.drop('empty', axis=1)
        df.insert(0, 'region_id', region_id, True)
        df['Week'] = df['Week'].astype(int)
        frames.append(df)
    
    result = pd.concat(frames).drop_duplicates().reset_index(drop=True)
    result = result.loc[(result.region_id != 12) & (result.region_id != 20)]
    return result

df = create_data_frame('./data')

reg_id_name = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська', 16: 'Рівненська',
    17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 21: 'Хмельницька', 22: 'Черкаська',
    23: 'Чернівецька', 24: 'Чернігівська'
}

st.title("Аналіз індексів VCI, TCI, VHI")

index_option = st.selectbox("Виберіть індекс:", ['VCI', 'TCI', 'VHI'])
region_option = st.selectbox("Виберіть область:", list(reg_id_name.values()))
year_range = st.slider("Виберіть діапазон років:", min_value=1981, max_value=2024, value=(2000, 2024))
week_range = st.slider("Виберіть діапазон тижнів:", min_value=1, max_value=52, value=(1, 52))

ascending = st.checkbox("Сортувати за зростанням")
descending = st.checkbox("Сортувати за спаданням")

df_filtered = df[(df['Year'].astype(int).between(*year_range)) &
                  (df['Week'].between(*week_range)) &
                  (df['region_id'] == list(reg_id_name.keys())[list(reg_id_name.values()).index(region_option)])]

if ascending and not descending:
    df_filtered = df_filtered.sort_values(by=index_option, ascending=True)
elif descending and not ascending:
    df_filtered = df_filtered.sort_values(by=index_option, ascending=False)

tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік часу", "Порівняльний графік"])

with tab1:
    st.write("### Відфільтровані дані")
    st.dataframe(df_filtered)

with tab2:
    st.write(f"### Часовий ряд {index_option} для {region_option}")
    fig, ax = plt.subplots()
    sns.lineplot(data=df_filtered, x='Week', y=index_option, ax=ax)
    st.pyplot(fig)

with tab3:
    st.write(f"### Порівняння {index_option} для {region_option} з іншими областями")
    df_comp = df[(df['Year'].astype(int).between(*year_range)) &
                  (df['Week'].between(*week_range))]
    fig, ax = plt.subplots()
    sns.boxplot(data=df_comp, x='region_id', y=index_option, ax=ax)
    ax.set_xticks(range(len(df_comp['region_id'].unique()))) 
    ax.set_xticklabels([reg_id_name.get(r, str(r)) for r in df_comp['region_id'].unique()], rotation=90)

    st.pyplot(fig)

if st.button("Скинути фільтри"):
    st.session_state['selected_variable'] = 'VHI'  
    st.session_state['selected_region'] = 'Вінницька' 
    st.session_state['week_range'] = (1, 52)  
    st.session_state['year_range'] = (1981, 2024)  
    st.session_state['sort_ascending'] = False 
    st.session_state['sort_descending'] = False 
    
    st.rerun() 
