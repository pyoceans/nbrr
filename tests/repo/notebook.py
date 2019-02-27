# In[ ]:


import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wget

dates = pd.date_range("2018-01-01", "2018-12-31", freq="D")
data = np.random.randn(len(dates))


# In[ ]:


with matplotlib.style.context("dark_background"):
    fig, ax = plt.subplots()
    l = ax.plot(dates, data)


# In[ ]:


get_ipython().system("tree data | head -10")


# In[ ]:
