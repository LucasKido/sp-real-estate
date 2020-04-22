import streamlit as st 
import pandas as pd 
import numpy as np
import joblib as jb
from scrap import *
from typing import Optional
import markdown

enc = jb.load('onehot_20200419.pkl.z')
rf = jb.load('model_20200419.pkl.z')

class Grid:
    """A (CSS) Grid"""

    def __init__(
        self,
        template_columns="1 1 1",
        gap="10px",
        background_color='purple',
        color='#fff',
    ):
        self.template_columns = template_columns
        self.gap = gap
        self.background_color = background_color
        self.color = color
        self.cells: List[Cell] = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        st.markdown(self._get_grid_style(), unsafe_allow_html=True)
        st.markdown(self._get_cells_style(), unsafe_allow_html=True)
        st.markdown(self._get_cells_html(), unsafe_allow_html=True)

    def _get_grid_style(self):
        return f"""
<style>
    .wrapper {{
    display: grid;
    grid-template-columns: {self.template_columns};
    grid-gap: {self.gap};
    background-color: {self.background_color};
    color: {self.color};
    }}
    .box {{
    background-color: {self.color};
    color: {self.background_color};
    border-radius: 5px;
    padding: 20px;
    font-size: 150%;
    }}
    table {{
        color: {self.color}
    }}
</style>
"""

    def _get_cells_style(self):
        return (
            "<style>"
            + "\n".join([cell._to_style() for cell in self.cells])
            + "</style>"
        )

    def _get_cells_html(self):
        return (
            '<div class="wrapper">'
            + "\n".join([cell._to_html() for cell in self.cells])
            + "</div>"
        )

    def cell(
        self,
        class_: str = None,
        grid_column_start: Optional[int] = None,
        grid_column_end: Optional[int] = None,
        grid_row_start: Optional[int] = None,
        grid_row_end: Optional[int] = None,
    ):
        cell = Cell(
            class_=class_,
            grid_column_start=grid_column_start,
            grid_column_end=grid_column_end,
            grid_row_start=grid_row_start,
            grid_row_end=grid_row_end,
        )
        self.cells.append(cell)
        return cell

class Cell:
    """A Cell can hold text, markdown, plots etc."""

    def __init__(
        self,
        class_: str = None,
        grid_column_start: Optional[int] = None,
        grid_column_end: Optional[int] = None,
        grid_row_start: Optional[int] = None,
        grid_row_end: Optional[int] = None,
    ):
        self.class_ = class_
        self.grid_column_start = grid_column_start
        self.grid_column_end = grid_column_end
        self.grid_row_start = grid_row_start
        self.grid_row_end = grid_row_end
        self.inner_html = ""

    def _to_style(self) -> str:
        return f"""
.{self.class_} {{
    grid-column-start: {self.grid_column_start};
    grid-column-end: {self.grid_column_end};
    grid-row-start: {self.grid_row_start};
    grid-row-end: {self.grid_row_end};
}}
"""

    def text(self, text: str = ""):
        self.inner_html = text

    def markdown(self, text):
        self.inner_html = markdown.markdown(text)

    def _to_html(self):
        return f"""<div class="box {self.class_}">{self.inner_html}</div>"""


def show_apes(dataframe):
    if dataframe.shape[0]>0:
        card = []
        for key, values in dataframe.iterrows():
            url = "<a href=https://www.quintoandar.com.br/imovel/{}</a>"
            ap_url = url.format(values['ap_id'])
            if len(values['address'])<=15:
                add = 15 - len(values['address'])
                new_add = values['address'] + (' '*add)
            else:
                new_add = values['address'][:15]
            textin = "<font size=3>{address}<br>{district}<br>Área: {area} m2<br>Quartos: {rooms}<br>Aluguel: {rent}<br>{link}Link</font>"
            card.append(textin.format(address=new_add,
                                      district=values['district'],
                                      area=values['area'],
                                      rooms=values['rooms'],
                                      rent=values['rent'],
                                      link=ap_url))

        with Grid("1 1 1", color='purple', background_color="#fff") as grid:
            if (len(card))>=3:
                grid.cell('a', 1, 2, 1, 5).text(card[0])
                grid.cell('b', 3, 4, 1, 5).text(card[1])
                grid.cell('c', 5, 6, 1, 5).text(card[2])
            elif len(card)==2:
                grid.cell('a', 1, 2, 1, 5).text(card[0])
                grid.cell('b', 3, 4, 1, 5).text(card[1])
                grid.cell('c', 5, 6, 1, 5).text('')
            else:
                grid.cell('a', 1, 2, 1, 5).text(card[0])
                grid.cell('b', 3, 4, 1, 5).text('')
                grid.cell('c', 5, 6, 1, 5).text('')
    else:
    	with Grid("1 1 1", color='purple', background_color="#fff") as grid:
            grid.cell(1, 2, 1, 2).text('Nenhum apartamento foi achado')

def sidebar():
    bairros = pd.read_csv('district.csv')
    st.sidebar.title('Parâmetros')
    neg_type = st.sidebar.selectbox('Compra/Aluga',['Aluguel', 'Compra'])
    district = st.sidebar.selectbox('Bairro', bairros['District'].unique())
    st.sidebar.markdown('Distância do metro [Km]')
    dist_min = st.sidebar.number_input('Distância mínima', min_value=0.01)
    dist_max = st.sidebar.number_input('Distância máxima', min_value=0.01, value=1.5)
    st.sidebar.markdown('Tamanho [m2]')
    size_max = st.sidebar.number_input('Tamanho máximo', min_value=20, value=80)
    size_min = st.sidebar.number_input('Tamanho mínimo', min_value=20, value=20)
    rooms = st.sidebar.number_input('Quartos', min_value=1, max_value=10, value=1)
    toilets = st.sidebar.number_input('Banheiros', min_value=1, max_value=10, value=1)
    suites = st.sidebar.number_input('Suítes', min_value=0, max_value=5, value=0)
    parking = st.sidebar.number_input('Vagas de estacionamento', min_value=0, max_value=3, value=0)
    elevator = st.sidebar.checkbox('Elevador', value=False)
    furnished = st.sidebar.checkbox('Mobiliado', value=False)
    sw_pool = st.sidebar.checkbox('Piscina', value=False)
    new = st.sidebar.checkbox('Novo', value=False)
    return [size_min, size_max, rooms, toilets, suites, parking, elevator, furnished, sw_pool, new, district, neg_type, dist_min, dist_max]

def conv_bool(feature):
	return 1 if feature==True else 0

def preprocessing(data):
	cat_cols = ['Negotiation Type', 'District']
	elevator = conv_bool(data[6])
	furnished = conv_bool(data[7])
	sw_pool = conv_bool(data[8])
	new = conv_bool(data[9])
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

def show_map(dataframe):
    ap_coord = []
    for coord in dataframe['local']:
        lat, lon = coord.split(',')
        ap_coord.append([float(lat), float(lon)])
    ap_coord = pd.DataFrame(ap_coord, columns=['latitude', 'longitude'])
    st.map(ap_coord, zoom=20)

def main():
    st.title('Prevendo o valor de um apartamento em SP')
    side_opt = sidebar()
    options = preprocessing(side_opt)
    predictions = prediction(options)
    st.markdown('{} no valor entre R$ {} ~ R$ {}'.format(side_opt[11], predictions[0].round(2), predictions[1].round(2)))
    apartamentos = ap_available(side_opt)
    show_apes(apartamentos)
    st.subheader('Mapa com os apartamentos')
    show_map(apartamentos)

main()