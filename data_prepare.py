import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from traceback import format_exc

def optimize_frame_memory(
    frame : pd.DataFrame
)-> pd.DataFrame:
    """
        Оптимизация объёма памяти датафрейма
        Parameters:
        ----------
        frame : датафрейм для оптимизации
    """
    try:
        float64_columns = frame.select_dtypes(
            include='float64'
        ).columns
        # преобразовываем столбцы с типом данных для чисел с плавающей запятой
        for float64_col in float64_columns:
            frame[float64_col]=frame[float64_col].astype('float32')
        int64_columns=frame.select_dtypes(
            include='int64'
        ).columns
        for int64_col in int64_columns:
            type_check_list=list(
                (frame[int64_col]>2147483648)&(frame[int64_col]<-2147483648)
            )
            # если ни один элемент в колонке не выходит за пределы int32, приводим к нему
            if not any(type_check_list):
                frame[int64_col]=frame[int64_col].astype('int32')
            else:
                pass
        object_columns = frame.select_dtypes(
            include='object'
        ).columns
        for object_col in object_columns:
            num_unique_values=len(frame[object_col].unique())
            num_total_values=len(frame[object_col])
            # если соотношение уникальных значений к общему количеству меньше 50%, преобразовываем к типу category
            if num_unique_values/num_total_values<0.5:
                frame[object_col]=frame[object_col].astype('category')
    except:
        print(f'В ходе работы функции произошла ошибка {format_exc()}')
    return frame

def look_memory_usage(
    frame : pd.DataFrame
)->str:
    try:
        if isinstance(frame, pd.DataFrame):
            usage_b = frame.memory_usage(deep=True).sum()
        else:
            usage_b = frame.memory_usage(deep=True)
        usage_mb = usage_b/1024**2
        response_string = '{:03.2f} Mb'.format(usage_mb)
    except:
        response_string = f'В ходе работы функции произошла ошибка: {format_exc()}'
    return response_string