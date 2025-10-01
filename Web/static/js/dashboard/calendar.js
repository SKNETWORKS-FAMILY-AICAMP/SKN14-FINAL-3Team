// KB국민은행 직원 업무시스템 - 캘린더 JavaScript

class Calendar {
    constructor() {
        this.currentYear = new Date().getFullYear();
        this.currentMonth = new Date().getMonth() + 1;
        this.renderCalendar();
    }
    
    // 월 이동 함수 (페이지 새로고침 없이)
    changeMonth(direction) {
        this.currentMonth += direction;
        if (this.currentMonth > 12) {
            this.currentMonth = 1;
            this.currentYear++;
        } else if (this.currentMonth < 1) {
            this.currentMonth = 12;
            this.currentYear--;
        }
        
        this.renderCalendar();
    }
    
    // 달력 렌더링
    renderCalendar() {
        const monthTitle = document.querySelector('.calendar-month');
        const calendarDays = document.getElementById('calendar-days');
        
        if (monthTitle) {
            monthTitle.textContent = `${this.currentYear}년 ${this.currentMonth}월`;
        }
        
        if (calendarDays) {
            const calendar = this.generateCalendar(this.currentYear, this.currentMonth);
            let html = '';
            
            calendar.forEach(week => {
                week.forEach(day => {
                    if (day === 0) {
                        html += '<div class="calendar-day empty"></div>';
                    } else {
                        const dateStr = `${this.currentYear}-${this.currentMonth.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
                        const isToday = this.isToday(this.currentYear, this.currentMonth, day);
                        
                        html += `<div class="calendar-day ${isToday ? 'today' : ''}" data-date="${dateStr}">
                            <span class="day-number">${day}</span>
                        </div>`;
                    }
                });
            });
            
            calendarDays.innerHTML = html;
        }
    }
    
    // 달력 데이터 생성 (월요일 시작)
    generateCalendar(year, month) {
        const firstDay = new Date(year, month - 1, 1);
        const startDate = new Date(firstDay);
        
        // 월요일로 조정
        const dayOfWeek = firstDay.getDay();
        const mondayOffset = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        startDate.setDate(firstDay.getDate() - mondayOffset);
        
        const calendar = [];
        const currentDate = new Date(startDate);
        
        // 6주 생성
        for (let week = 0; week < 6; week++) {
            const weekDays = [];
            for (let day = 0; day < 7; day++) {
                if (currentDate.getMonth() === month - 1) {
                    weekDays.push(currentDate.getDate());
                } else {
                    weekDays.push(0);
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
            calendar.push(weekDays);
        }
        
        return calendar;
    }
    
    // 오늘 날짜 확인
    isToday(year, month, day) {
        const today = new Date();
        return today.getFullYear() === year && 
               today.getMonth() + 1 === month && 
               today.getDate() === day;
    }
}

// 전역 함수로 월 이동 버튼 연결
function changeMonth(direction) {
    if (window.calendar) {
        window.calendar.changeMonth(direction);
    }
}

// DOM 로드 완료 후 초기화
document.addEventListener('DOMContentLoaded', function() {
    window.calendar = new Calendar();
});
