def runrate(df=None, column=None):
   '''
   '''
   df = df

   return df


def resample(df=None, column=None, resolution='D'):
   '''
   '''
   df = df.resample(resolution).agg({column: ['mean', 'std', 'median']})

   return df
