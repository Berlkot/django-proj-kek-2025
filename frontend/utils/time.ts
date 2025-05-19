// frontend/utils/time.ts
export const formatTimeAgo = (dateString?: string): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.round((now.getTime() - date.getTime()) / 1000);

  if (isNaN(seconds) || seconds < 0) { // Проверка на невалидную дату или дату из будущего
      const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
      try {
        return new Date(dateString).toLocaleDateString('ru-RU', options); // Фоллбэк на простой формат даты
      } catch (e) {
        return "Неверная дата";
      }
  }

  const minutes = Math.round(seconds / 60);
  const hours = Math.round(minutes / 60);
  const days = Math.round(hours / 24);
  const months = Math.round(days / 30.44); // Среднее количество дней в месяце
  const years = Math.round(days / 365.25); // Учет високосных годов

  if (seconds < 60) return `${seconds} сек. назад`;
  if (minutes < 60) return `${minutes} мин. назад`;
  if (hours < 24) return `${hours} ч. назад`;
  if (days < 30) return `${days} дн. назад`;
  if (months < 12) return `${months} мес. назад`;
  return `${years} г. назад`;
};


export const formatDate = (dateString?: string): string => {
  if (!dateString) return 'Дата не указана';
  try {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return date.toLocaleDateString('ru-RU', options);
  } catch (e) {
    console.error("Error formatting date:", e);
    return "Неверная дата";
  }
};