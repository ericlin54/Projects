import numpy as np
from hmmlearn import hmm
import pandas as pd
import pickle
import math
import matplotlib.pyplot as plt
from sklearn.utils import check_random_state
from sklearn.metrics import mean_absolute_error

# CONSTANTS
# import pdb; pdb.set_trace()
EPSILON = 0.0001
NUM_BUCKETS = 5
NUM_HIDDEN_STATES = 15
BUCKET_C = 0.01
NUM_ITERS = 1000
PICKLE_PATH = "./model.pkl"
STOCK_DATA_PATH = "./sp500_stock_data"
STOCK_INDUSTRY_DATA_PATH = "./industry_data"

def plot_timeseries(series, title="No Title"):
    x = np.arange(len(series))
    plt.title(title)
    plt.plot(x, series)
    plt.show()

def find_bounds(series, init_floor=-1, init_ceil=1, containment=0.90):
    N = len(series)
    _floor, _ceil = init_floor, init_ceil
    curr_containment = N + 1

    while curr_containment > int(containment * N):
        _floor += EPSILON / 2
        _ceil -= EPSILON / 2
        curr_containment = (
            (_floor < series) & (series < _ceil)
        ).sum()

    return _floor, _ceil

def logdata(d):
    return np.log(np.abs(d) + 1) * np.sign(d)

def const_to_discrete(s):
    return np.floor(s * NUM_BUCKETS)

def price_data_to_obs(DATA):
    DIFF = np.diff(DATA) / DATA[-1]
    DIFF_FLOOR, DIFF_CEIL = find_bounds(DIFF, containment=0.99)
    CLIPPED_DIFF = np.clip(DIFF, DIFF_FLOOR, DIFF_CEIL)
    return DIFF

def build_model(DATA_TRAIN, pickle_path):
    try:
        model = pickle.load(open(pickle_path, "rb"))
        print("Succesfully loaded model!")
    except:
        model = hmm.GaussianHMM(
            n_components=NUM_HIDDEN_STATES,
            covariance_type="tied",
            tol = 0.001,
            n_iter = NUM_ITERS,
            params='stmc'
        )
        model.fit(DATA_TRAIN)
        print("Pickling hmm model to {}".format(pickle_path))
        pickle.dump(model, open(pickle_path, 'wb'))
        print("Done pickling")
    return model

def get_train_test_data(sym, percent=0.05):
    bin_file = open(STOCK_DATA_PATH, 'rb')
    sp500_stocks, stock_data = pickle.load(bin_file)
    bin_file.close()

    if False:
        bin_file = open(STOCK_INDUSTRY_DATA_PATH, 'rb')
        industry_data = pickle.load(bin_file)
        bin_file.close()

        sector = sp500_stocks.loc[sp500_stocks['Symbol'] == sym]['Sector'].iloc[0]
        SECTOR_DATA = industry_data[sector][['Open', 'Close', 'High', 'Low', 'Volume']]

    # sp500_stocks: Dictionary of all of the stocks
    # Each stock has its lettered key Ex: Google has key 'GOOGL'

    DATA = stock_data[sym][['Open', 'Close', 'High', 'Low', 'Volume']]

    # Multiply by splits so stock splits don't change company value
    splits = np.cumprod(stock_data[sym]['Split Ratio'])
    DATA['Open'] = DATA['Open'] * splits
    DATA['Close'] = DATA['Close'] * splits
    DATA['High'] = DATA['High'] * splits
    DATA['Low'] = DATA['Low'] * splits
    DATA['Volume'] = DATA['Volume'] / splits
    max_volume = np.max(DATA['Volume'])
    old_volume = DATA['Volume'].copy()[1:].reset_index()['Volume'] / max_volume

    N = len(DATA['Open'])
    np.random.seed(42)

    OBS_DATA = DATA.apply(price_data_to_obs)
    OBS_DATA['Volume'] = old_volume

    plot_timeseries(OBS_DATA['Volume'], 'Volume')

    # Only train on first 95% of Data, predict last 5%
    frac = int(math.ceil(percent * N))
    return OBS_DATA[:-frac], OBS_DATA[-frac:], DATA

def get_next_pred_state(model, DATA_EST):
    hidden_states = model.predict(DATA_EST)
    transmat_cdf = np.cumsum(model.transmat_, axis=1)
    random_state = check_random_state(model.random_state)
    next_state = (transmat_cdf[hidden_states[-1]] > random_state.rand()).argmax()
    return next_state

def get_next_obs(model, DATA_EST):
    hidden_states = model.predict(DATA_EST)
    transmat_cdf = np.cumsum(model.transmat_, axis=1)
    random_state = check_random_state(model.random_state)
    next_state = (transmat_cdf[hidden_states[-1]] > random_state.rand()).argmax()
    next_obs = model._generate_sample_from_state(
        next_state, random_state)
    return next_obs

def calc_error(DATA_EST, predictions):
    return mean_absolute_error(
        DATA_EST['Open'], predictions['Open']
    )
    # N = DATA_EST.shape[0]
    # sums = predictions.subtract(DATA_EST).abs().sum(axis=0)
    # return sums

def forecast_stock(sym):
    pickle_path = "{}_model.pkl".format(sym)
    DATA_TRAIN, DATA_EST, DATA_REAL = get_train_test_data(sym)
    TRAIN_LEN, TEST_LEN = len(DATA_TRAIN), len(DATA_EST)
    model = build_model(DATA_TRAIN, pickle_path)
    hidden_states = model.predict(DATA_EST)

    pred_data = np.apply_along_axis(
        lambda x: model.means_[x], 0, hidden_states
    )

    train_empty = pd.DataFrame(
        np.nan,
        index=range(TRAIN_LEN),
        columns=['Open', 'Close', 'High', 'Low', 'Volume']
    )
    test_empty = pd.DataFrame(
        np.nan,
        index=range(TEST_LEN),
        columns=['Open', 'Close', 'High', 'Low', 'Volume']
    )
    pred_df = pd.DataFrame(
        pred_data,
        columns=['Open', 'Close', 'High', 'Low', 'Volume']
    )

    predictions = pd.concat(
        (train_empty, pred_df)
    )
    test_data = pd.concat(
        (train_empty, DATA_EST)
    )
    train_data = pd.concat(
        (DATA_TRAIN, test_empty)
    )

    print("ERROR AMOUNT: {}".format(
        calc_error(DATA_EST, pred_df))
    )

    real_data = np.array(DATA_REAL['Open'][:-1])
    predictions_real = real_data + predictions['Open'] * real_data

    x = np.arange(len(DATA_TRAIN) + len(DATA_EST))
    plt.plot(x, DATA_REAL['Open'][:-1])
    plt.plot(x, predictions_real)
    plt.legend([
        'DATA_REAL',
        'predictions'
    ])
    plt.show()

forecast_stock("AAPL")
