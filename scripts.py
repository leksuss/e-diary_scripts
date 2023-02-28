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
        subject__title=subject.title,
    ).order_by('?').first()

    commendation_text = random.choice(COMMENDATION_TEXTS)

    Commendation.objects.create(
        text=commendation_text,
        created=random_lesson.date,
        schoolkid=schoolkid,
        subject=random_lesson.subject,
        teacher=random_lesson.teacher,
    )


def ask_schoolkid():

    msg = ('Напиши имя ученика, данные которого мы будем улучшать:\n')
    asked_schoolkid_name = input(msg).strip().title()

    try:
        schoolkid = Schoolkid.objects.get(
            full_name__contains=asked_schoolkid_name,
        )
    except Schoolkid.MultipleObjectsReturned:
        print('\nЯ нашел много учеников с таким именем.')
        return None
    except Schoolkid.DoesNotExist:
        print('\nК сожалению, я не нашел ученика с таким именем.')
        return None

    return schoolkid


def ask_action():

    printed_actions = []
    for num, variant in actions().items():
        printed_actions.append(f'{num}. {variant["msg"]}\n')

    msg = '\nЧто мы сегодня будем улучшать? Напиши номер действия:\n'

    action_number = input(f'{msg}{"".join(printed_actions)}')
    if action_number not in actions():
        print('\nК сожалению, ты ввел неверный номер.')
        return None
    return action_number


def ask_subject(schoolkid):

    msg = '\nУкажи предмет урока, для которого нужно написать похвалу:\n'
    subject_name = input(msg).strip().title()
    try:
        subject_obj = Subject.objects.get(
            title=subject_name,
            year_of_study=schoolkid.year_of_study,
        )
    except Subject.DoesNotExist:
        print('\nК сожалению, я не нашел этот предмет.')
        return None
    return subject_obj


def run():

    print('Приветствую тебя, мой юный хакер!')

    schoolkid_obj = ask_schoolkid()
    if schoolkid_obj is None:
        print('Запусти скрипт еще раз.')
        return None

    action = ask_action()
    if action is None:
        print('Запусти скрипт еще раз.')
        return None

    args = {}
    if actions()[action]['extra_arg_funcs']:
        for arg_name, arg_func in actions()[action]['extra_arg_funcs'].items():
            args[arg_name] = arg_func(schoolkid_obj)
            if args[arg_name] is None:
                print('Запусти скрипт еще раз.')
                return None

    actions()[action]['func'](schoolkid_obj, **args)
    print('\nОтлично, мы это сделали! Если хочешь исправить записи'
          'другого ученика, запусти скрипт снова.\n')
