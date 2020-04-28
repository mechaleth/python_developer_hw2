# -*- coding: utf-8 -*-
import datetime
import logging
import os.path

import pandas

from homework import assistive


class PatientFieldsValueError(ValueError):
    def __init__(self, logger, message, *args):
        super(PatientFieldsValueError, self).__init__()
        print(type(logger))
        logger.error(message + ":" + str(args))


class PatientFieldsTypeError(TypeError):
    def __init__(self, logger: logging.RootLogger, message: str, *args: object) -> object:
        super(PatientFieldsTypeError, self).__init__()
        logger.error(message + ":" + str(args))


class PatientFieldsAttributeError(AttributeError):
    def __init__(self, logger: logging.RootLogger, message: str, *args: object) -> object:
        super(PatientFieldsAttributeError, self).__init__()
        logger.error(message + ":" + str(args))


def set_decorator(set_funct, self_value_to_set_name: str, logger_name: str, *set_funct_args):
    """возвращает функцию set(self,value) для property с проверками, выполняемыми
    в функции set_funct для проверяемого значения self_value_to_set_name, изменяемого
    в словаре объекта посредством set_value_to_dict_funct"""
    def set_wrapper(self, value):
        checked_value = set_funct(self, value, *set_funct_args)
        self.__dict__[self_value_to_set_name] = checked_value
        logger = self.__dict__[logger_name]
        if type(logger) is logging.Logger:
            logger.info("Person's field %s was setted" % (self_value_to_set_name), *set_funct_args)
    return set_wrapper


def get_decorator(self_value_to_get_name: str):
    """возвращает функцию get(self) для property для значения self_value_to_get_name,
    получаемого из словаря объекта посредством get_value_from_dict_func"""
    def get_wrapper(self):
        return self.__dict__[self_value_to_get_name]
    return get_wrapper


class Patient:
    __PHONE_SIGNIFICANT_DIGITS_NUMBER = 10
    __UNIVERAL_INNER_PHONE_CODE = "8"
    __RUSSIAN_PHONE_CODE = "+7"
    __ALSO_RUSSIAN_PHONE_CODE = "7"
    __PHONE_FORMAT = "{0}-{1}{2}{3}-{4}{5}{6}-{7}{8}-{9}{10}"
    __PASSPORT_DOCUMENT_TYPE = "паспорт"
    __FOREIGN_PASSPORT_DOCUMENT_TYPE = "заграничный паспорт"
    __DRIVER_LICENSE_DOCUMENT_TYPE = "водительское удостоверение"
    __PASSPORT_DIGITS_AMOUNT = 10
    __FOREIGN_PASSPORT_DIGIT_AMOUNT = 9
    __DRIVER_LICENSE_DIGIT_AMOUNT = 10
    __passport_format = "{0}{1}{2}{3} {4}{5}{6}{7}{8}{9}"
    __foreign_passport_format = "{0}{1} {2}{3}{4}{5}{6}{7}{8}"
    __driver_license_format = "{0}{1} {2}{3} {4}{5}{6}{7}{8}{9}"

    __birth_date_format = "%Y-%m-%d"
    # множество цифр
    __STRING_NUMBER_SET = set([str(i) for i in range(10)])
    # множество допустимых символов документов, кроме цифр
    __DOCUMENTS_ALLOW_SYMBOLS_SET = {" ","-","/"}
    # множество допустимых символов дат рождений, кроме цифр
    __BIRTH_DATE_ALLOW_SYMBOLS_SET = {"-", ".", "/"}
    # множество допустимых символов телефонного номера, кроме цифр
    __PHONE_ALLOW_SYMBOLS_SET = {"(", "-", ")"}

#    __patient_logging = PatientLoggingDescriptor()

    @classmethod
    def create(cls, first_name=None, last_name=None, birth_date=None, \
               phone=None, document_type=None, document_id=None):
        return cls(first_name, last_name, birth_date, phone, document_type, document_id)


    def __init__(self, first_name=None, last_name=None, birth_date=None, \
                 phone=None, document_type=None, document_id=None):
        self.mine_good_logger = logging.getLogger(assistive.goodname)
        self.mine_bad_logger = logging.getLogger(assistive.badname)
        if self.input_none_check(first_name, last_name, birth_date, phone, document_type, document_id):
            self.__create(first_name, last_name, birth_date, phone, document_type, document_id)

    def __del__(self):
        del self.mine_good_logger
        del self.mine_bad_logger
        for namelist in [assistive.goodname, assistive.badname]:
            for handlerr in list(logging.getLogger(namelist).handlers)[::-1]:
                handlerr.close()

    def input_none_check(self, first_name, last_name, birth_date, \
                         phone, document_type, document_id):
        meaning_dict = {"first name": first_name, "last name": last_name, "birth date": birth_date, \
                        "phone": phone, "document type": document_type, "document id": document_id}
#        self.mine_good_logger.info("Check dict %s" % meaning_dict)
        none_check = False
        mean_check = False
        none_str = str()
        for key, value in meaning_dict.items():
            if value is None:
                none_check = True
                none_str += key
                none_str += " "
            else:
                mean_check = True
            # self.mine_good_logger.info(
            #    "value of {} is {}, nonecheck is {}, meancheck is {}".format(key, value, none_check, mean_check))
        # self.mine_good_logger.info("Final nonecheck is {}, meancheck is {}".format(none_check, mean_check))
        if (none_check is True) & (mean_check is False):
            # self.mine_good_logger.info("All input values is None")
            return False
        elif (none_check is False) & (mean_check is True):
            # self.mine_good_logger.info("All input values is not None")
            return True
        else:
            # Часть значений заполнена, часть нет
            #            self.mine_bad_logger.info("Some inputs are None: ", none_str)
            #            raise TypeError()
            raise PatientFieldsTypeError(self.mine_bad_logger, "Some inputs are None: ", none_str)

    def type_monitoring(self, value, data_type, log_message, error_message):
        if type(value) is not data_type:
            # ошибка типа данных
            #            self.mine_bad_logger.info("Error data type"+error_message, value)
            #            raise TypeError()
            raise PatientFieldsTypeError(self.mine_bad_logger, "Error data type " + error_message, value)

    def __create(self, first_name, last_name, birth_date, \
                 phone, document_type, document_id):
        self.__first_name = self.__set_name(first_name, "first_name")
        self.__last_name  = self.__set_name(last_name, "last_name")
        self.__birth_date = self.__set_birth_date(birth_date)
        self.__phone      = self.__set_phone(phone)
        self.__document_type = self.__set_document_type(document_type)
        self.__document_id   = self.__set_document_id(document_id)
        self.mine_good_logger.info("Person %s %s created" % (self.__first_name, self.__last_name))

    def __fall_if_set_name(self, name: str, name_field_name: str):
        raise PatientFieldsAttributeError(self.mine_bad_logger, "Error in case set %s forbid" % name_field_name, name)

    def __set_name(self, name: str, name_field_name: str) -> str:
        self.type_monitoring(name, str, "Error during {} check".format(name_field_name),
                             "Set {} error".format(name_field_name))
        # имя состоит из букв
        if name.isalpha():
            # self.mine_good_logger.info("Person %s %s add" % (name_field_name, name))
            # Начинается с большой буквы имя!
            return name.title()
        else:
            # у нас ошибка, следует ее залогировать в файл
            raise PatientFieldsValueError(self.mine_bad_logger, \
                                          "Set %s value error: unexpected chars" % name_field_name, name)

    def __set_phone(self, telephone_number: str) -> str:
        # допустимые варианты:
        # 1.  89000000000 - только цифры и 8
        # 2. +79000000000 - почти как вариант 1
        # 3.  8(900)0000000
        # 4. +7(900)0000000
        # 5.  8-900-000-00-00
        # 6.  8-900-000-0000
        # 7. +7-900-000-0000
        # 8.  8(900)000-00-00
        # 9. +7(900)000-00-00
        # 10. 8(900)000-0000
        # 11.+7(900)000-0000
        # 12.+7-900-000-00-00 - номинальный
        log_error_message = "Error during phone number check"
        self.type_monitoring(telephone_number, str, log_error_message, "Phone is not str")
        country_code = str()
        phone_without_code = str()
        code_len = 0
        # номер начинается с кода
        if telephone_number.startswith(self.__UNIVERAL_INNER_PHONE_CODE):
            code_len = len(self.__UNIVERAL_INNER_PHONE_CODE)
            country_code = self.__RUSSIAN_PHONE_CODE
        elif telephone_number.startswith(self.__RUSSIAN_PHONE_CODE):
            code_len = len(self.__RUSSIAN_PHONE_CODE)
            country_code = self.__RUSSIAN_PHONE_CODE
        elif telephone_number.startswith(self.__ALSO_RUSSIAN_PHONE_CODE):
            code_len = len(self.__ALSO_RUSSIAN_PHONE_CODE)
            country_code = self.__RUSSIAN_PHONE_CODE
        else:
            # Нужно добавить код в допустимые
            # а пока...
            #  Ошибка кода номера телефона!
            raise PatientFieldsValueError(self.mine_bad_logger, "Invalid phone %s number code" % telephone_number)
        # телефон без кода страны
        phone_without_code = telephone_number[code_len:len(telephone_number)]
        # все допустимые символы
        full_allowable_set = self.__STRING_NUMBER_SET.union(self.__PHONE_ALLOW_SYMBOLS_SET)
        # Если в номере присутствуют недопустимые символы
        if not set(phone_without_code).issubset(full_allowable_set):
            # Ошибка номера телефона!
            raise PatientFieldsTypeError(self.mine_bad_logger,
                                         "Invalid character in phone %s number" % telephone_number)
        # Телефонный номер с цифрами
        pure_number = list()
        # счетчик для подсчета цифр в номере телефона
        nums_count = 0
        for char in phone_without_code:
            # нас интересуют только цифры
            if set(char).issubset(self.__STRING_NUMBER_SET):
                nums_count += 1
                if nums_count <= self.__PHONE_SIGNIFICANT_DIGITS_NUMBER:
                    pure_number.append(char)
                else:
                    raise PatientFieldsValueError(self.mine_bad_logger, \
                                                  "More than limit for digits in phone %s number. Limit is %i" \
                                                  % (telephone_number, self.__PHONE_SIGNIFICANT_DIGITS_NUMBER))
        formatted_phone = self.__PHONE_FORMAT.format(country_code, *pure_number)
        # self.mine_good_logger.info("Person's phone %s added" % formatted_phone)
        # переводим в требуемый формат
        return formatted_phone

    def __set_birth_date(self, birth_date: str) -> str:
        # Допустимые варианты
        # 1. 1978-01-31
        # 2. 1978.01.31
        # 3. 31.01.1978
        # 4. 31-01-1978
        # 5. 31/01/1978
        # у даты 3 составляющие - день, месяц, год
        log_error_message = "Error during birth date check"
        self.type_monitoring(birth_date, str, log_error_message, "Invalid data type in birth date")
        DATE_CONSISTANT_AMOUNT = 3
        YEAR_NUM_AMOUNT = 4
        # все допустимые символы
        full_allowable_set = self.__STRING_NUMBER_SET.union(self.__BIRTH_DATE_ALLOW_SYMBOLS_SET)
        # Если в номере присутствуют недопустимые символы
        if not set(birth_date).issubset(full_allowable_set):
            # Ошибка даты рождения!
            #            self.mine_bad_logger.info("Invalid character in birth %s date" % birth_date)
            #            raise ValueError()
            raise PatientFieldsValueError(self.mine_bad_logger, "Invalid character in birth date", birth_date)
        date_list = list()
        split_char = str()
        for char in self.__BIRTH_DATE_ALLOW_SYMBOLS_SET:
            if char in birth_date:
                date_list = birth_date.split(char)
                split_char = char
                break
        # разделители должны быть однообразны
        if len(date_list) < DATE_CONSISTANT_AMOUNT:
            # Ошибка даты рождения!
            raise PatientFieldsValueError(self.mine_bad_logger, "Invalid format of the birth date", birth_date)
        if len(date_list[-1]) == YEAR_NUM_AMOUNT:
            input_format = "%d{}%m{}%Y".format(split_char, split_char)
        elif len(date_list[0]) == YEAR_NUM_AMOUNT:
            input_format = "%Y{}%m{}%d".format(split_char, split_char)
        else:
            # год не первый и не последний
            raise PatientFieldsValueError(self.mine_bad_logger, "Invalid consistant order in birth date", birth_date)
        formatted_birth_date = str()
        try:
            date_of_birth = datetime.datetime.strptime(birth_date, input_format)
            formatted_birth_date = datetime.datetime.strftime(date_of_birth, self.__birth_date_format)
        except Exception as exx:
            # Ошибка даты рождения!
            raise PatientFieldsValueError(self.mine_bad_logger, str(exx) + " in the birth date " + str(birth_date))
        # self.mine_good_logger.info("Person's birth date %s added" % formatted_birth_date)
        return formatted_birth_date

    @staticmethod
    def __document_type_check(document_type: str, default_document_type: str) -> bool:
        # множество букв, встречающихся в default_document_type
        document_char_set = set(default_document_type).union(default_document_type.upper())
        return set(document_type).issubset(document_char_set)

    def __set_document_type(self, document_type: str) -> str:
        log_error_message = "Error during document type check"
        self.type_monitoring(document_type, str, log_error_message, "Document type type error")
        formatted_document_type = str()
        if self.__document_type_check(document_type, self.__PASSPORT_DOCUMENT_TYPE):
            # они имели в виду паспорт, но ошиблись или лень
            formatted_document_type = self.__PASSPORT_DOCUMENT_TYPE
        elif self.__document_type_check(document_type, self.__DRIVER_LICENSE_DOCUMENT_TYPE):
            # они имели в виду водительское удостоверение, но ошиблись или лень
            formatted_document_type = self.__DRIVER_LICENSE_DOCUMENT_TYPE
        elif self.__document_type_check(document_type, self.__FOREIGN_PASSPORT_DOCUMENT_TYPE):
            # они имели в виду загранпаспорт, но ошиблись или лень
            formatted_document_type = self.__FOREIGN_PASSPORT_DOCUMENT_TYPE
        else:
            # не понятно, что они имели в виду
            raise PatientFieldsValueError(self.mine_bad_logger, "Unable to understand type of document", document_type)
        # self.mine_good_logger.info("Person's document type %s added" % formatted_document_type)
        return formatted_document_type

    def __set_document_id(self, document_number: str) -> str:
        # Допустимые варианты
        # для паспорта
        # 4000 000000 - 10 цифр, номинальный
        # для водительского удостоверения
        # 00 00 000000 - 10 цифр, номинальный
        # 0000 000000
        # загранпаспорт
        # 00 0000000 - 9 цифр, номинальный
        # 000000000
        # все допустимые символы
        log_error_message = "Error  document type during document id check"
        self.type_monitoring(document_number, str, log_error_message, "Document id type error")
        document_id = str()
        # паспорт
        if self.__document_type == self.__PASSPORT_DOCUMENT_TYPE:
            document_id = self.return_id_or_raise_exeption(document_number, self.__PASSPORT_DIGITS_AMOUNT, \
                                                           self.__DOCUMENTS_ALLOW_SYMBOLS_SET, self.__passport_format)
        elif self.__document_type == self.__FOREIGN_PASSPORT_DOCUMENT_TYPE:
            document_id = self.return_id_or_raise_exeption(document_number, self.__FOREIGN_PASSPORT_DIGIT_AMOUNT, \
                                                           self.__DOCUMENTS_ALLOW_SYMBOLS_SET,\
                                                           self.__foreign_passport_format)
        elif self.__document_type == self.__DRIVER_LICENSE_DOCUMENT_TYPE:
            document_id = self.return_id_or_raise_exeption(document_number, self.__DRIVER_LICENSE_DIGIT_AMOUNT, \
                                                           self.__DOCUMENTS_ALLOW_SYMBOLS_SET,\
                                                           self.__driver_license_format)
        else:
            # ошибка типа документа
            raise PatientFieldsValueError(self.mine_bad_logger, "Uncorrect document type given", self.__document_type)
        # self.mine_good_logger.info("Person's document id %s added" % document_id)
        return document_id

    def return_id_or_raise_exeption(self, id: str, demand_id_digit_number: str, allowable_signs_set: set, \
                                    doc_format: str) -> str:
        full_allowable_set = self.__STRING_NUMBER_SET.union(allowable_signs_set)
        # Если в номере присутствуют недопустимые символы
        if not set(id).issubset(full_allowable_set):
            # Ошибка номера документа!
            #            self.mine_bad_logger.info("Invalid character in document %s id" % id)
            #            raise ValueError()
            raise PatientFieldsValueError(self.mine_bad_logger, "Invalid character in document %s id" % id)
        # только цифры
        pure_number = id
        for char in allowable_signs_set:
            # удаляем символ из строки
            unchar_str = pure_number.replace(char,"")
            pure_number = unchar_str
            del unchar_str
        if len(pure_number) == demand_id_digit_number:
            return doc_format.format(*pure_number)
        else:
            raise PatientFieldsValueError(self.mine_bad_logger, \
                                          "Id %s of %s document not formattable" % (id, self.__document_type))

    # поля property
    document_id = property(get_decorator("_Patient__document_id"), \
                           set_decorator(__set_document_id, "_Patient__document_id", "mine_good_logger"))
    first_name = property(get_decorator("_Patient__first_name"), \
                          set_decorator(__fall_if_set_name, "_Patient__first_name", "mine_good_logger", "first_name"))
    last_name = property(get_decorator("_Patient__last_name"), \
                         set_decorator(__fall_if_set_name, "_Patient__last_name", "mine_good_logger", "last_name"))
    birth_date = property(get_decorator("_Patient__birth_date"), \
                          set_decorator(__set_birth_date, "_Patient__birth_date", "mine_good_logger"))
    phone = property(get_decorator("_Patient__phone"), set_decorator(__set_phone, "_Patient__phone", "mine_good_logger"))
    document_type = property(get_decorator("_Patient__document_type"), \
                             set_decorator(__set_document_type, "_Patient__document_type", "mine_good_logger"))

    # save this object to csv-file
    def save(self):
        # self.mine_good_logger.info("Saving patient to file")
        patient_dict = {"birth date": self.__birth_date, "phone": self.__phone, \
                        "document type": self.__document_type, "document id": self.__document_id}
        patient_index = pandas.MultiIndex.from_tuples([(self.__last_name, self.__first_name)])
        patient_index.names = ["last name", "first name"]
        patient_data_frame = pandas.DataFrame([patient_dict], index=patient_index)
        patient_data_frame.columns.names = ["Patients data"]
        # Если файл существует и не пуст, строку надо добавить
        # Если не существует, надо создать
        if os.path.exists(assistive.zombie_base_file):
            if os.path.getsize(assistive.zombie_base_file) > 0:
                self.mine_good_logger.info("Zombie file already exist")
                current_data_frame = pandas.read_csv(assistive.zombie_base_file, index_col=["last name", "first name"],\
                                                     encoding="utf-8")
                self.mine_good_logger.info("Zombie file reads")
                if current_data_frame.merge(patient_data_frame).empty:
                    patient_data_frame = current_data_frame.append(patient_data_frame)
                    # patient_data_frame = patient_data_frame.sort_index()
                    self.mine_good_logger.info("Patient added, table sorted by last name/first name")
                else:
                    # данный поциент уже есть
                    self.mine_good_logger.info("Patient already exist")
                    return
        patient_data_frame.to_csv(assistive.zombie_base_file, mode="w", encoding="utf-8")
        self.mine_good_logger.info("File updated")


class PatientCollection:
    __inner_patient_list = list()
    __inner_patient_list_counter = 0
    __common_byte_counter = 0
    __common_line_number = 0

    def __init__(self, path_to_file):
        # существует ли данный файл?
        if os.path.exists(path_to_file):
            # файл существует
            self.myfile = path_to_file
            self.my_file_size = os.path.getsize(path_to_file)
            # logging.info("File %s exists" % path_to_file)
        else:
            #            logging.info("File %s not exists" % path_to_file)
            raise Exception("File not exists")
        if ".csv" not in path_to_file:
            #            logging.info("File %s type error" % path_to_file)
            raise ValueError("File type error")
        self.__inner_dict_filler()

    def __del__(self):
        for i in range(len(self.__inner_patient_list)):
            del self.__inner_patient_list[0]

    def __inner_dict_filler(self):
        patient_data_frame = pandas.read_csv(self.myfile)
        for index, row in patient_data_frame.iterrows():
            self.__inner_patient_list.append(Patient(first_name=row["first name"], last_name=row["last name"], \
                                                     birth_date=row["birth date"], phone=row["phone"], \
                                                     document_type=row["document type"],
                                                     document_id=row["document id"]))

    def __iter__(self):
        return self

    def __inner_list_updater(self, patient, index):
        if index < len(self.__inner_patient_list):
            del self.__inner_patient_list[index]
        self.__inner_patient_list.insert(index, patient)

    def __next__(self):
        if self.__common_byte_counter < os.path.getsize(self.myfile):
            with open(self.myfile, "rb") as file:
                # прочитанные байты - не в счет
                file.seek(self.__common_byte_counter)
                for byte_line in file:
                    self.__common_line_number += 1
                    self.__common_byte_counter += len(byte_line)
                    # первая линия - заголовок
                    if self.__common_line_number > 1:
                        patient = self.patient_creation_from_bytestr(byte_line, encoding="utf-8")
                        # строки считаем от 1+1 строка заголовочная
                        self.__inner_list_updater(patient, self.__common_line_number - 2)
                        return patient
        self.__common_line_number = 0
        self.__common_byte_counter = 0
        raise StopIteration

    @staticmethod
    def patient_creation_from_bytestr(bstring: bytes, encoding: str = "utf-8") -> Patient:
        # декодируем бинарную строку
        dec_string = bstring.decode(encoding=encoding)
        # удаляем каретки, если таковые имеются
        str_without_r = dec_string.replace("\r", "")
        del dec_string
        # удаляем перенос на следующую строку и разбиваем на массив слов
        str_list = str_without_r.replace("\n", "").split(",")
        del str_without_r
        return Patient(last_name=str_list[0], first_name=str_list[1], \
                       birth_date=str_list[2], phone=str_list[5], \
                       document_type=str_list[4], document_id=str_list[3])

    def limit(self, number_limits: int):
        count = 0
        if type(number_limits) is not int:
            raise TypeError("Invalid number limits type")
        if number_limits < 0:
            raise ValueError("Negative number limits")
        if number_limits == 0:
            return
        with open(self.myfile, "rb") as file:
            for line in file:
                if count > 0:
                    patient = self.patient_creation_from_bytestr(line, encoding="utf-8")
                    # нулевая линия - заголовок
                    self.__inner_list_updater(patient, count - 1)
                    yield patient
                count += 1
                if count > number_limits:
                    break

    def __len__(self):
        return len(self.__inner_patient_list)

    def __getitem__(self, item):
        return self.__inner_patient_list.__getitem__(int(item))

    def __contains__(self, item: Patient):
        if type(item) is Patient:
            for patient in self.__inner_patient_list:
                last_name_check = item.last_name is patient.last_name
                first_name_check = item.first_name is patient.first_name
                birth_date_check = item.birth_date is patient.birth_date
                document_type_check = item.document_type is patient.document_type
                document_id_check = item.document_id is patient.document_id
                phone_check = item.phone is patient.phone
                #                print("last_name_check {} item {} patient {}".format(last_name_check, item.last_name, patient.last_name))
                #                print("first_name_check {} item {} patient {}".format(first_name_check, item.first_name, patient.first_name))
                #                print("birth_date_check {} item {} patient {}".format(birth_date_check, item.birth_date, patient.birth_date))
                #                print("document_id_check {} item {} patient {}".format(document_id_check, item.document_id, patient.document_id))
                #                print("document_type_check {} item {} patient {}".format(document_type_check, item.document_type, patient.document_type))
                #                print("phone_check {} item {} patient {}".format(phone_check, item.phone, patient.phone))
                if (last_name_check & first_name_check & birth_date_check & document_type_check & \
                            document_id_check & phone_check):
                    return True
        return False
