import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import axios from 'axios';
import ReactStars from 'react-rating-stars-component';
import '@fullcalendar/common/main.css';
import '@fullcalendar/daygrid/main.css';

const FoodCalendar = () => {
  const [events, setEvents] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [formData, setFormData] = useState({
    type: 'feed',
    productName: '',
    purchaseLink: '',
    rating: 0,
    previousFood: '',
    quantityKg: '',
    durationDays: ''
  });
  const [dailyConsumption, setDailyConsumption] = useState(0);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [prevOptions, setPrevOptions] = useState([]);

  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (formData.quantityKg && formData.durationDays) {
      const daily = parseFloat(formData.quantityKg) / parseFloat(formData.durationDays);
      setDailyConsumption(isNaN(daily) ? 0 : daily.toFixed(2));
    } else setDailyConsumption(0);
  }, [formData.quantityKg, formData.durationDays]);

  useEffect(() => {
    const options = events
      .filter(evt => evt.extendedProps.type === formData.type)
      .map(evt => evt.extendedProps.productName)
      .filter((v, i, a) => a.indexOf(v) === i);
    setPrevOptions(options);
  }, [events, formData.type]);

  const fetchEvents = async () => {
    try {
      const res = await axios.get('/api/food-events');
      const loaded = res.data.map(evt => {
        const icon = evt.type === 'feed' ? '🥣' : '🍖';
        const color = evt.type === 'feed' ? '#4CAF50' : '#FF9800';
        return {
          id: evt.id,
          title: `${icon} ${evt.productName}`,
          start: evt.date,
          backgroundColor: color,
          extendedProps: { ...evt }
        };
      });
      setEvents(loaded);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDateClick = (info) => {
    setSelectedDate(info.dateStr);
    setFormData({ ...formData, date: info.dateStr });
    setIsEditMode(false);
    setSelectedEventId(null);
  };

  const handleEventClick = (info) => {
    const { id, extendedProps } = info.event;
    setSelectedEventId(id);
    setSelectedDate(extendedProps.date);
    setFormData({
      type: extendedProps.type,
      productName: extendedProps.productName,
      purchaseLink: extendedProps.purchaseLink,
      rating: extendedProps.rating,
      previousFood: extendedProps.previousFood,
      quantityKg: extendedProps.quantityKg,
      durationDays: extendedProps.durationDays
    });
    setIsEditMode(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleRatingChange = (newRating) => {
    setFormData({ ...formData, rating: newRating });
  };

  const handleSave = async () => {
    const payload = { date: selectedDate, ...formData };
    try {
      if (isEditMode) {
        await axios.put(`/api/food-events/${selectedEventId}`, payload);
      } else {
        await axios.post('/api/food-events', payload);
      }
      fetchEvents();
      setFormData({ type: 'feed', productName: '', purchaseLink: '', rating: 0, previousFood: '', quantityKg: '', durationDays: '' });
      setDailyConsumption(0);
      setIsEditMode(false);
      setSelectedEventId(null);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async () => {
    if (!selectedEventId) return;
    try {
      await axios.delete(`/api/food-events/${selectedEventId}`);
      fetchEvents();
      setFormData({ type: 'feed', productName: '', purchaseLink: '', rating: 0, previousFood: '', quantityKg: '', durationDays: '' });
      setDailyConsumption(0);
      setIsEditMode(false);
      setSelectedEventId(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '70% 30%', height: '100vh' }}>
      <div>
        <FullCalendar
          plugins={[dayGridPlugin]}
          initialView="dayGridMonth"
          events={events}
          dateClick={handleDateClick}
          eventClick={handleEventClick}
        />
      </div>
      <div style={{ padding: '1rem', borderLeft: '1px solid #ddd' }}>
        <h3>{isEditMode ? '이벤트 수정' : '이벤트 추가'}</h3>
        <div>
          <label>날짜:</label>
          <input type="date" name="date" value={selectedDate} readOnly />
        </div>
        <div>
          <label>타입:</label>
          <select name="type" value={formData.type} onChange={handleInputChange}>
            <option value="feed">사료</option>
            <option value="snack">간식</option>
          </select>
        </div>
        <div>
          <label>상품명:</label>
          <input type="text" name="productName" value={formData.productName} onChange={handleInputChange} />
        </div>
        <div>
          <label>구매처 링크:</label>
          <input type="text" name="purchaseLink" value={formData.purchaseLink} onChange={handleInputChange} />
        </div>
        <div>
          <label>만족도:</label>
          <ReactStars count={5} value={formData.rating} onChange={handleRatingChange} size={24} activeColor="#ffd700" />
        </div>
        <div>
          <label>이전 섭취 사료:</label>
          <select name="previousFood" value={formData.previousFood} onChange={handleInputChange}>
            <option value="">선택하세요</option>
            {prevOptions.map((opt, idx) => (
              <option key={idx} value={opt}>{opt}</option>
            ))}
          </select>
        </div>
        <div>
          <label>구매량(kg):</label>
          <input type="number" step="0.01" name="quantityKg" value={formData.quantityKg} onChange={handleInputChange} />
        </div>
        <div>
          <label>소비 기간(일):</label>
          <input type="number" name="durationDays" value={formData.durationDays} onChange={handleInputChange} />
        </div>
        <div>
          <label>일일 섭취량(kg):</label>
          <input type="text" value={dailyConsumption} readOnly />
        </div>
        <button onClick={handleSave} style={{ marginRight: '0.5rem' }}>{isEditMode ? '수정' : '저장'}</button>
        {isEditMode && <button onClick={handleDelete}>삭제</button>}
      </div>
    </div>
  );
};

export default FoodCalendar; 