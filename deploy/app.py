import streamlit as st 
import pandas as pd 
import numpy as np
import joblib as jb

enc = jb.load('onehot_20200419.pkl.z')
rf = jb.load('model_20200419.pkl.z')

def start():
	df = pd.read_csv('district.csv')

def sidebar():
	bairros = pd.read_csv('district.csv')
	st.sidebar.title('Parâmetros')
	neg_type = st.sidebar.selectbox('Compra/Aluga',['Aluguel', 'Compra'])
	district = st.sidebar.selectbox('Bairro', bairros['District'].unique())
	st.sidebar.markdown('Distância do metro [Km]')
	dist_min = st.sidebar.number_input('Distância mínima', min_value=0.01)
	dist_max = st.sidebar.number_input('Distância máxima', min_value=0.01, value=0.5)
	st.sidebar.markdown('Tamanho [m2]')
	size_max = st.sidebar.number_input('Tamanho máximo', min_value=20, value=50)
	size_min = st.sidebar.number_input('Tamanho mínimo', min_value=20, value=20)
	rooms = st.sidebar.number_input('Quartos', min_value=1, max_value=10, value=1)
	toilets = st.sidebar.number_input('Banheiros', min_value=1, max_value=10, value=1)
	suites = st.sidebar.number_input('Suítes', min_value=0, max_value=5, value=0)
	parking = st.sidebar.number_input('Vagas de estacionamento', min_value=0, max_value=10, value=0)
	elevator = st.sidebar.checkbox('Elevador', value=False)
	furnished = st.sidebar.checkbox('Mobiliado', value=False)
	sw_pool = st.sidebar.checkbox('Piscina', value=False)
	new = st.sidebar.checkbox('Novo', value=False)
	return [size_min, size_max, rooms, toilets, suites, parking, elevator, furnished, sw_pool, new, district, neg_type, dist_min, dist_max]

def conv_bool(feature):
	return True if feature==1 else False

def preprocessing(data):
	cat_cols = ['Negotiation Type', 'District']
	elevator = data[6]
	furnished = data[7]
	sw_pool = data[8]
	new = data[9]
	neg_type = 'rent' if data[11]=='Aluguel' else 'sale'
	df = pd.DataFrame({'Size':[data[0], data[1]],
	                   'Rooms':[data[2], data[2]],
                       'Toilets':[data[3], data[3]],
	                   'Suites':[data[4], data[4]],
	                   'Parking':[data[5], data[5]],
	                   'Elevator':[elevator, elevator],
	                   'Furnished':[furnished, furnished],
	                   'Swimming Pool':[sw_pool, sw_pool],
	                   'New':[new, new],
	                   'District':[data[10], data[10]],
	                   'Negotiation Type':[neg_type, neg_type],
	                   'Dist2Subway':[data[13], data[12]]})
	cat_feat = enc.transform(df[cat_cols])
	cat_feat = pd.DataFrame(cat_feat)
	cat_feat.columns = enc.get_feature_names(cat_cols)
	num_feat = df.drop(cat_cols, axis=1)
	df = pd.merge(cat_feat, num_feat, left_index=True, right_index=True)
	# st.write(df)
	return df

def prediction(dataframe):
	y_pred = rf.predict(dataframe)
	return y_pred

def main():
	st.title('Prevendo o valor de um apartamento em SP')
	side_opt = sidebar()
	predictions = prediction(preprocessing(side_opt))
	st.markdown('{} no valor entre R$ {} ~ R$ {}'.format(side_opt[11], predictions[0].round(2), predictions[1].round(2)))

main()