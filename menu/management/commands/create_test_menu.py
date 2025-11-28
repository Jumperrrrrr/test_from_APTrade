from django.core.management.base import BaseCommand
from menu.models import Menu, MenuItem


class Command(BaseCommand):
    help = 'Создает тестовое меню для проверки работы приложения'

    def handle(self, *args, **options):
        menu, created = Menu.objects.get_or_create(name='main_menu')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создано меню: {menu.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Меню {menu.name} уже существует. Удаляем старые пункты...'))
            MenuItem.objects.filter(menu=menu).delete()

        items_data = [
            {'title': 'Главная', 'url': '/', 'named_url': 'home', 'order': 0, 'parent': None},
            {'title': 'Страница 1', 'url': '', 'named_url': 'page1', 'order': 1, 'parent': None},
            {'title': 'Страница 2', 'url': '', 'named_url': 'page2', 'order': 2, 'parent': None},
            {'title': 'Страница 3', 'url': '/page3/', 'named_url': 'page3', 'order': 3, 'parent': None},
        ]

        created_items = {}
        
        for item_data in items_data:
            parent = item_data.pop('parent')
            item = MenuItem.objects.create(
                menu=menu,
                parent=parent,
                **item_data
            )
            created_items[item_data['title']] = item
            self.stdout.write(f'  Создан пункт: {item.title}')

        page1 = created_items['Страница 1']
        sub_items_1 = [
            {'title': 'Подстраница 1.1', 'url': '/page1/', 'named_url': 'page1', 'order': 0, 'parent': page1},
            {'title': 'Подстраница 1.2', 'url': '/page1/sub1/', 'named_url': 'page1_sub1', 'order': 1, 'parent': page1},
            {'title': 'Подстраница 1.3', 'url': '/page1/sub2/', 'named_url': 'page1_sub2', 'order': 2, 'parent': page1},
        ]

        for item_data in sub_items_1:
            parent = item_data.pop('parent')
            item = MenuItem.objects.create(
                menu=menu,
                parent=parent,
                **item_data
            )
            self.stdout.write(f'  Создан пункт: {item.title} (под {parent.title})')

        page2 = created_items['Страница 2']
        sub_items_2 = [
            {'title': 'Подстраница 2.1', 'url': '/page2/', 'named_url': 'page2', 'order': 0, 'parent': page2},
            {'title': 'Подстраница 2.2', 'url': '/page2/sub1/', 'named_url': 'page2_sub1', 'order': 1, 'parent': page2},
        ]

        for item_data in sub_items_2:
            parent = item_data.pop('parent')
            item = MenuItem.objects.create(
                menu=menu,
                parent=parent,
                **item_data
            )
            self.stdout.write(f'  Создан пункт: {item.title} (под {parent.title})')

        sub1_1 = MenuItem.objects.get(title='Подстраница 1.1', menu=menu)
        sub_sub_items = [
            {'title': 'Подподстраница 1.1.1', 'url': '/page1/sub1/', 'named_url': '', 'order': 0, 'parent': sub1_1},
            {'title': 'Подподстраница 1.1.2', 'url': '/page1/sub2/', 'named_url': '', 'order': 1, 'parent': sub1_1},
        ]

        for item_data in sub_sub_items:
            parent = item_data.pop('parent')
            item = MenuItem.objects.create(
                menu=menu,
                parent=parent,
                **item_data
            )
            self.stdout.write(f'  Создан пункт: {item.title} (под {parent.title})')

        category_item = MenuItem.objects.create(
            menu=menu,
            title='Категории',
            url='',
            named_url='',
            order=4,
            parent=None
        )
        self.stdout.write(f'  Создан пункт: {category_item.title}')

        category_sub_items = [
            {'title': 'Категория 1', 'url': '/category/1/', 'named_url': '', 'order': 0, 'parent': category_item},
            {'title': 'Категория 2', 'url': '/category/2/', 'named_url': '', 'order': 1, 'parent': category_item},
            {'title': 'Категория 3', 'url': '/category/3/', 'named_url': '', 'order': 2, 'parent': category_item},
        ]

        for item_data in category_sub_items:
            parent = item_data.pop('parent')
            item = MenuItem.objects.create(
                menu=menu,
                parent=parent,
                **item_data
            )
            self.stdout.write(f'  Создан пункт: {item.title} (под {parent.title})')

        self.stdout.write(self.style.SUCCESS(f'\nТестовое меню "{menu.name}" успешно создано!'))
        self.stdout.write(f'Всего создано пунктов: {MenuItem.objects.filter(menu=menu).count()}')
