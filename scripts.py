import random

from datacenter.models import (Chastisement, Commendation, Lesson, Mark,
                               Schoolkid, Subject)


COMMENDATION_TEXTS = [
    'Молодец!',
    'Отлично!',
    'Хорошо!',
    'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!',
    'Великолепно!',
    'Прекрасно!',
    'Ты меня очень обрадовал!',
    'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!',
    'Ты, как всегда, точен!',
    'Очень хороший ответ!',
    'Талантливо!',
    'Ты сегодня прыгнул выше головы!',
    'Я поражен!',
    'Уже существенно лучше!',
    'Потрясающе!',
    'Замечательно!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!',
]


def actions():

    return {
        '1': {
            'msg': 'Исправить все двойки и тройки на пятерки',
            'func': fix_marks,
            'extra_arg_funcs': None,
        },
        '2': {
            'msg': 'Удалить все замечания',
            'func': remove_chastisements,
            'extra_arg_funcs': None,
        },
        '3': {
            'msg': 'Написать похвалу к случайному уроку по нужному предмету',
            'func': create_commendation,
            'extra_arg_funcs': {
                'subject': ask_subject,
            }
        },
    }


def fix_marks(schoolkid):

    Mark.objects.filter(
        schoolkid=schoolkid,
        points__lt=4,
    ).update(
        points=5,
    )


def remove_chastisements(schoolkid):

    chastisements = Chastisement.objects.filter(
        schoolkid=schoolkid,
    )

    chastisements.delete()


def create_commendation(schoolkid, subject):

    random_lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title=subject,
    ).order_by('?')

    commendation_text = random.choice(COMMENDATION_TEXTS)

    Commendation.objects.create(
        text=commendation_text,
        created=random_lesson.date,
        schoolkid=schoolkid,
        subject=random_lesson.subject,
        teacher=random_lesson.teacher,
    )


def get_schoolkids(schoolkid_name):

    schoolkids = Schoolkid.objects.filter(
        full_name__contains=schoolkid_name,
    )
    return schoolkids


def ask_schoolkid():

    msg = ('\nНапиши имя ученика, данные которого мы будем улучшать:\n')

    while True:
        schoolkid_name = input(msg).strip().title()
        if not schoolkid_name:
            msg = ('\nХорошо бы все-таки написать имя :) \n'
                   'Попробуй еще раз:\n')
            continue
        schoolkids = get_schoolkids(schoolkid_name)
        if not schoolkids:
            msg = ('\nК сожалению, я не нашел ученика с таким именем.\n'
                   'Может, ты ошибся в написании? Попробуй еще раз:\n')
            continue
        if schoolkids.count() > 1:
            msg = ('\nЯ нашел больше чем одного ученика с таким именем.\n'
                   'Попробуй уточнить, добавив фамилию и/или отчество:\n')
            continue
        break
    return schoolkids.first()


def ask_action():

    printed_actions = []
    for num, variant in actions().items():
        printed_actions.append(f'{num}. {variant["msg"]}\n')

    msg = '\nЧто мы сегодня будем улучшать? Напиши номер действия:\n'
    while True:
        action_number = input(f'{msg}{"".join(printed_actions)}')
        if action_number not in actions():
            msg = f'\nПожалуйста, введи верный номер:\n'
            continue
        break
    return action_number


def get_subject(subject_name):

    subject_obj = Subject.objects.filter(
        title=subject_name,
    ).first()
    if subject_obj:
        return subject_obj.title
    return False


def ask_subject():

    msg = '\nУкажи предмет урока, для которого нужно написать похвалу:\n'
    while True:
        subject_name = input(msg).strip().title()
        subject_obj = get_subject(subject_name)
        if not subject_obj:
            msg = ('\nК сожалению, я не нашел этот предмет.\n'
                   'Пожалуйста, напиши правильный предмет:\n')
            continue
        break
    return subject_obj


def run():

    print('Приветствую тебя, мой юный хакер!')
    while True:
        schoolkid_obj = ask_schoolkid()
        action = ask_action()
        args = {}
        if actions()[action]['extra_arg_funcs']:
            for arg_name, arg_func in actions()[action]['extra_arg_funcs'].items():
                args[arg_name] = arg_func()
        actions()[action]['func'](schoolkid_obj, **args)
        msg = ('\nОтлично, мы это сделали!\n'
               'Хочешь хакнуть записи другого ученика? Просто нажми "Enter"\n'
               'Если на сегодня всё, то отправь букву "q"\n')
        whats_next = input(msg).strip()
        if not whats_next:
            continue
        print('\nВозвращайся еще! Отметки сами себя не исправят!')
        break
