# In[ ]:


import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

dates = pd.date_range("2018-01-01", "2018-12-31", freq="D")
rng = np.random.default_rng()
data = rng.normal(size=len(dates))


# In[ ]:


with mpl.style.context("dark_background"):
    fig, ax = plt.subplots()
    ax.plot(dates, data)


# In[ ]:


get_ipython().system("tree data | head -10")  # noqa: F821


# In[ ]:
