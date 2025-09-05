import datetime

import streamlit as st
import sql
import telebot
from messages import messages
import random

users = sql.Users.get_list()
exercises = sql.Exercises.get_list_works()

users_selector = st.selectbox("Подопечный", users)
start_date = st.date_input("Дата тренировки", key="start", format='DD/MM/YYYY')

plan = sql.Plan.get_df(username=users_selector, date=start_date)[["exercise_name", "weight_steps_repeats"]]

plan_table = st.dataframe(plan,
                          column_config={"exercise_name": st.column_config.Column("Упражнение"),
                                         "weight_steps_repeats": st.column_config.Column("Вес/Повторения/Подходы"),
                                         }, key="in")


@st.dialog("Добавление упражнения")
def add_exercise(user, date):
    exercise_selector = st.selectbox("Упражнение", exercises, key="ex_add_sel")
    comment_input = st.text_input("Вес/Повторения/Подходы", key="ex_add_comm")
    if st.button("Добавить", key="add_exercise_accept"):
        sql.Plan.add_record(
            date=date,
            username=user,
            exercise_name=exercise_selector,
            weight_steps_repeats=comment_input
        )
        st.rerun()


@st.dialog("Удаление упражнения")
def delete_exercise(user, date, exercises_lst):
    selector = st.selectbox("Упражнение", exercises_lst)
    if st.button("Удалить", key="ex_del_accept"):
        sql.Plan.delete_record(
            date=date,
            username=user,
            exercise_name=selector
        )
        st.rerun()


with st.container(border=True, width=230):
    if st.button("Добавить упражнение", width=200):
        add_exercise(users_selector, start_date)
    if st.button("Удалить упражнение", width=200):
        exercises_list = list(plan["exercise_name"])
        delete_exercise(users_selector, start_date,exercises_list)
    if st.button("Отправить уведомление", width=200):
        token = st.secrets["tg_bot"]["token"]
        bot = telebot.TeleBot(token)
        tg_id = sql.Users.get_tg_id(users_selector)
        formatted = start_date.strftime("%d.%m.%y")
        first_part = random.choice(messages)
        second_part = f"\nПлан тренировки на {formatted} ждет тебя 💪\nМожешь смотреть 👌"
        message_text = first_part + second_part
        bot.send_message(tg_id, message_text)
        st.toast("Функция\n<Пнуть жиробасика>\nуспешно выполнена")
