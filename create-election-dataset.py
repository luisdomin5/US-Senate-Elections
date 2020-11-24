## Create election dataset

import pandas as pd


# Process candidates parties
def candidates_data():
    
    headers = ['CAND_ID', 'CAND_NAME', 'CAND_PTY_AFFILIATION', 'CAND_ELECTION_YR', 
               'CAND_OFFICE_ST', 'CAND_OFFICE', 'CAND_OFFICE_DISTRICT', 'CAND_ICI',
               'CAND_STATUS', 'CAND_PCC', 'CAND_ST1', 'CAND_ST2', 'CAND_CITY',
               'CAND_ST', 'CAND_ZIP']
    
    candidates = pd.DataFrame()
    for y in range(2000,2021,2):
        df = pd.read_csv("data/candidates/cn{}/cn.txt".format(str(y)[-2:]), sep="|", header=None)
        df.columns = headers
        df = df[['CAND_ID', 'CAND_PTY_AFFILIATION']]
        df['year'] = y
        df = df.drop_duplicates()
        candidates = candidates.append(df)
    
    return candidates


# Process voting results
def results_data():
    
    # file sheet names
    files = {2002:("2002fedresults.xls", '2002 House & Senate Results'),
             2004:("federalelections2004.xls", '2004 US HOUSE & SENATE RESULTS'),
             2006:("federalelections2006.xls", '2006 US House & Senate Results'),
             2008:("federalelections2008.xls", '2008 House and Senate Results'),
             2010:("federalelections2010.xls", '2010 US House & Senate Results'),
             2012:("federalelections2012.xls", '2012 US House & Senate Resuts'),
             2014:("federalelections2014.xls", '2014 US Senate Results by State'),
             2016:("federalelections2016.xlsx", '2016 US Senate Results by State'),
             2018:("federalelections2018.xlsx", '2018 US Senate Results by State')}
    
    # process and append data
    results = pd.DataFrame()
    for year in files:
    
        # read in annual file
        df = pd.read_excel('data/results/'+files[year][0], sheet_name=files[year][1])
        
        # standardize columns
        if year == 2002:
            df = df.rename(columns={'STATE':'STATE ABBREVIATION'})       
        df = df.rename(columns={'INCUMBENT INDICATOR (I)':'(I)',
                                'CANDIDATE NAME (Last, First)':'CANDIDATE NAME',
                                'GENERAL ': 'GENERAL VOTES ',
                                'GENERAL':'GENERAL VOTES ',
                                'GENERAL RESULTS':'GENERAL VOTES ',
                                'PRIMARY':'PRIMARY VOTES',
                                'PRIMARY RESULTS':'PRIMARY VOTES',
                                'Candidate Name (Last)':'CANDIDATE NAME (Last)',
                                'FEC ID':'FEC ID#',
                                'INCUMBENT INDICATOR':'(I)',
                                'FIRST NAME':'CANDIDATE NAME (First)',
                                'LAST NAME':'CANDIDATE NAME (Last)',
                                'LAST NAME, FIRST':'CANDIDATE NAME',
                                'LAST NAME,  FIRST':'CANDIDATE NAME',
                                'D':'DISTRICT'})
    
        # drop total rows, limit to senate races 
        df = df.dropna(axis=0,subset=['STATE ABBREVIATION', 'FEC ID#'])
        df = df[df['DISTRICT']=='S']
        df = df[df['PARTY'].str[0]!='W']
        df['STATE ABBREVIATION'] = df['STATE ABBREVIATION'].str.replace(' ','')
        df = df[~df['PARTY'].isnull()]
        df = df[~df['PARTY'].str.contains('Combined Parties')]
        if year == 2004:
            df = df[df['CANDIDATE NAME']=='Said, Mohammad H.'] # data error. Total votes was entered in wrong cell
        
        # make incumbent indicator
        df['INCUMBENT'] = (df['(I)']=='(I)').astype(int)
        
        # select relevant columns
        df = df[['STATE ABBREVIATION', 'FEC ID#', 'INCUMBENT', 
                 'CANDIDATE NAME (First)', 'CANDIDATE NAME (Last)', 
                 'CANDIDATE NAME', 'PRIMARY VOTES', 'GENERAL VOTES ']]
           
        # split primary and election votes into separate rows     
        value_vars = ['PRIMARY VOTES', 'GENERAL VOTES ']
        id_vars = [x for x in df.columns if x not in value_vars]
        df = pd.melt(df,id_vars=id_vars, value_vars=value_vars, value_name='votes')
        df['ELECTION'] = df['variable'].apply(lambda x: x.split(' ')[0])
        def isnumber(x):
            try:
                float(x)
                return True
            except:
                return False
        df = df[df['votes'].apply(isnumber)]    
        id_vars.append('ELECTION')
        df.dropna(axis=0, inplace=True)
        df['year'] = year
        results = results.append(df)
    results['FEC ID#'] = results['FEC ID#'].str.replace(' ','')
        
    return results


# Process donation data
def donations_data():
    
    headers = ['CAND_ID', 'CAND_NAME', 'CAND_ICI', 'PTY_CD',
              'CAND_PTY_AFFILIATION', 'TTL_RECEIPTS', 'TRANS_FROM_AUTH',
              'TTL_DISB', 'TRANS_TO_AUTH', 'COH_BOP', 'COH_COP',
              'CAND_CONTRIB', 'CAND_LOANS', 'OTHER_LOANS',
              'CAND_LOAN_REPAY', 'OTHER_LOAN_REPAY', 'DEBTS_OWED_BY',
              'TTL_INDIV_CONTRIB', 'CAND_OFFICE_ST', 'CAND_OFFICE_DISTRICT',
              'SPEC_ELECTION', 'PRIM_ELECTION', 'RUN_ELECTION',
              'GEN_ELECTION', 'GEN_ELECTION_PRECENT',
              'OTHER_POL_CMTE_CONTRIB', 'POL_PTY_CONTRIB',
              'CVG_END_DT', 'INDIV_REFUNDS', 'CMTE_REFUNDS', ]
    
    donations = pd.DataFrame()
    for y in range(1980,2021,2):
        df = pd.read_csv("data/donations/weball{}.txt".format(str(y)[-2:]), sep="|", header=None)
        df.columns = headers
        df['year'] = y
        donations = donations.append(df)
        
    donations = donations[['CAND_ID','TTL_RECEIPTS','year']]   
        
    return donations


# Process census population estimates
def population_data():
    
    # population files
    pop19 = "data/population/nst-est2019-01.xlsx"
    pop09 = "data/population/st-est00int-01.xls"
    
    # merge files
    for file in [pop19, pop09]:
        df = pd.read_excel(file, header=3)
        df = df.iloc[5:56]
        df = df.rename(columns={'Unnamed: 0':'STATE'})
        df['STATE'] = df['STATE'].apply(lambda x: x[1:])
        if file == pop19:
            df.drop(['Census','Estimates Base'],axis=True,inplace=True)
            population = df
        else:
            df.drop(['Unnamed: 1', 'Unnamed: 12', 'Unnamed: 13'],axis=True,inplace=True)
            population = pd.merge(left=population,right=df,how='left',on='STATE')
    
    # get state name-abbreviation crosswalk from election data
    state_map = pd.read_excel('data/results/federalelections2012.xls', '2012 US House & Senate Resuts')
    state_map = state_map[['STATE',"STATE ABBREVIATION"]].drop_duplicates().dropna()
    state_map = {row['STATE']:row['STATE ABBREVIATION'] for (index,row) in state_map.iterrows()}
    population['STATE ABBREVIATION'] = population['STATE'].map(state_map)
    
    # reshape years long
    population = population.melt(id_vars=['STATE','STATE ABBREVIATION'],var_name='year',value_name='population')
    population.drop(['STATE'],axis=1,inplace=True)
    
    return population



def main():

    candidates = candidates_data()
    results = results_data()
    donations = donations_data()
    population = population_data()
    
    # Merge data together
    df = results[results['ELECTION']=='GENERAL']
    df = pd.merge(left=df, right=donations, how='left', 
             left_on=['FEC ID#','year'], right_on=['CAND_ID','year'])
    df['TTL_RECEIPTS'] = df['TTL_RECEIPTS'].fillna(0)
    df = pd.merge(left=df, right=candidates, how='inner',
                  left_on=['FEC ID#','year'], right_on=['CAND_ID','year'])
    df = pd.merge(left=df, right=population, how='inner',
                  left_on=['STATE ABBREVIATION','year'], right_on=['STATE ABBREVIATION','year'])
    
    # Limit to general election and find winner
    df = df[df['ELECTION']=='GENERAL']
    df['winner'] = df.groupby(['year','STATE ABBREVIATION'])['votes'].transform(max)==df['votes']
    df['winner'] = df['winner'].astype(int)
    
    # Remove elections won by non-Dem/Rep
    oth_win = df[((df['winner']==1) & (~df['CAND_PTY_AFFILIATION'].isin(['DEM','REP'])))][['STATE ABBREVIATION','year']]
    df = pd.merge(left=df,right=oth_win,how='left',on=['STATE ABBREVIATION','year'],indicator=True)
    df = df[df['_merge']=='left_only']
    df.drop('_merge',axis=1,inplace=True)
    df = df[df['CAND_PTY_AFFILIATION'].isin(['DEM','REP'])]
    
    # Check that there are two cands in each state-year
    df = df[~((df['STATE ABBREVIATION']=='LA') & (df['year']==2016))] # LA 2016 had no primary
    maxvotes = df.groupby(['STATE ABBREVIATION','year','CAND_PTY_AFFILIATION'])['votes'].transform(max) # candidate with most votes
    maxvotes = df[df['votes']==maxvotes][['STATE ABBREVIATION','year','population','CAND_PTY_AFFILIATION','CANDIDATE NAME']]
    maxvotes = maxvotes.set_index(['STATE ABBREVIATION','year','population','CAND_PTY_AFFILIATION'])
    grouped = df.groupby(['STATE ABBREVIATION','year','population','CAND_PTY_AFFILIATION'])
    df = grouped.agg({'INCUMBENT':'max','TTL_RECEIPTS':'sum','votes':'sum','winner':'max'})
    df = pd.merge(left=df,right=maxvotes,how='left',left_index=True,right_index=True)
    df = df.unstack().reset_index()
    df.dropna(axis=0,inplace=True)
    
    # Rename columns and save
    df = df.rename(columns={'STATE ABBREVIATION':'state','INCUMBENT':'incumbent'
                            , 'TTL_RECEIPTS':'spending','CANDIDATE NAME':'name'})
    df.to_csv('data/election-dataset.csv',index=False)
    
if __name__ == '__main__':
    main()
    
# EOF
