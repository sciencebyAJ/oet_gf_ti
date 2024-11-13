import pandas as pd
import glob
import numpy as np
import requests
import datetime
import json

class get_tower_data(object):
    def __init__(self,
                 filename,
                 in_dir,
                 out_dir,
                 open_et_api_key,
                 debug=False):

        self.file_name = filename
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.OET_apikey = open_et_api_key
        self.debug = debug

        ##
        self.in_fname = self.in_dir+self.file_name
        self.site_id = self.get_site_id()
        self.meta_df = self.get_meta()
        self.lat, self.lon = self.get_lat_lon_from_fname()
        self.site_df = self.read_data()
        self.start_time,self.end_time = self.get_start_end_times()
        self.site_oet_df = self.add_OpenET_df()
        self.site_all_df = self.add_aliased_df()


    def get_meta(self):
        '''
        returns metadata data for site
        '''
        site_meta_df = pd.read_excel(self.in_dir+'station_metadata.xlsx',skiprows=1)
        site_meta_df=site_meta_df.loc[site_meta_df['Site ID']==self.site_id]
        return site_meta_df

    def get_site_id(self):
        '''
        returns site_id
        '''
        return self.file_name.split('_daily')[0].split('/')[-1]

    def get_lat_lon_from_fname(self):
        '''
        returns lat and lon in decimal degrees for tower
        '''
        site_id = self.site_id
        site_meta_df = self.meta_df
        # site_meta_df.loc[site_meta_df['Site ID']==site_id]
        lat = site_meta_df['Latitude'].values[0]
        lon = site_meta_df['Longitude'].values[0]
        if self.debug==True:
          print(lat, lon)
        return lat, lon

    def read_data(self):
        '''
        returns site dataframe based on file name and path
        '''
        site_df= pd.read_csv(self.in_fname)
        site_df['date_index'] = pd.to_datetime(site_df['date'])
        site_df = site_df.set_index('date_index')
        site_df = site_df.loc[site_df.index>'2016']
        if self.debug==True:
          print(site_df.index.values[0], site_df.index.values[-1])
        return site_df

    def get_start_end_times(self):
        '''
        returns start and end times for site
        '''
        start_time = pd.Timestamp(self.site_df.index.values[0])
        end_time = pd.Timestamp(self.site_df.index.values[-1])
        # Now you can use strftime on the Timestamp object
        Stime_api = start_time.strftime('%Y-%m-%d')
        Etime_api = end_time.strftime('%Y-%m-%d')
        if self.debug==True:
          print(Stime_api, Etime_api)
        return Stime_api, Etime_api

    def call_OET_api_ET(self):
        # endpoint arguments
        # set your API key before making the request
        var="ET"
        header = {"Authorization" : self.OET_apikey}
        args = {
          "date_range": [self.start_time,self.end_time],
          "interval": "daily",
          "overpass": True,
          "geometry": [self.lon,self.lat],
          "model": "Ensemble",
          "reference_et": "gridMET",
          "units": "mm",
          "variable": var,
          "file_format": "json"
        }

        # query the api
        resp = requests.post(
            headers=header,
            json=args,
            url="https://openet-api.org/raster/timeseries/point"
        )
        #
        df_ET = pd.DataFrame(resp.json())
        df_ET['time'] = pd.to_datetime(df_ET["time"])
        df_ET = df_ET.set_index("time")
        return df_ET

    def call_OET_api_ETo(self):
        # endpoint arguments
        # set your API key before making the request
        var="ETo"
        header = {"Authorization" : self.OET_apikey}
        args = {
          "date_range": [self.start_time,self.end_time],
          "interval": "daily",
          "overpass": True,
          "geometry": [self.lon,self.lat],
          "model": "Ensemble",
          "reference_et": "gridMET",
          "units": "mm",
          "variable": var,
          "file_format": "json"
        }

        # query the api
        resp = requests.post(
            headers=header,
            json=args,
            url="https://openet-api.org/raster/timeseries/point"
        )
        #
        df_ETo = pd.DataFrame(resp.json())

        df_ETo['time'] = pd.to_datetime(df_ETo["time"])
        df_ETo.set_index("time",inplace=True)

        return df_ETo

    def add_OpenET_df(self):
        '''
        calls OpenET api to retrieve et, and eto
        creates clear-sky columns for ground obs too
        '''
        oet_df = self.call_OET_api_ET()
        if self.debug==True:
          print('et api call made')
        oeto_df = self.call_OET_api_ETo()
        if self.debug==True:
          print('eto api call made')
        merged_df=pd.merge(self.site_df,oet_df, how='outer', left_index=True, right_index=True)
        merged_df=pd.merge(merged_df,oeto_df, how='outer', left_index=True, right_index=True)
        merged_df['clear_sky_EToF'] = merged_df['EToF_filtered'].mask(np.isnan(merged_df['et']), np.nan)
        merged_df['clear_sky_ET'] = merged_df['ET_corr'].mask(np.isnan(merged_df['et']), np.nan)
        return merged_df

    def add_aliased_df(self):
        '''
        add aliased data to dataframe
        '''
        add_allias_df=self.site_oet_df.copy()
        if self.debug==True:
          print('adding aliased data')
        for i in [8,16,32]:
          self_dfX =self.site_df[::i].copy()
          self_dfX.rename(columns={'ET_corr':f'ET_corr{str(i)}'},inplace=True)
          add_allias_df = pd.merge(add_allias_df,self_dfX[[f'ET_corr{str(i)}']], how='outer', left_index=True, right_index=True)
        return add_allias_df
