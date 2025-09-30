// Todo Widget JavaScript
class TodoWidget {
    constructor() {
        this.todos = [];
        this.nextId = 4; // 다음 ID (현재 3개 아이템이 있으므로)
        this.init();
    }
    
    init() {
        this.loadTodos();
        this.setupEventListeners();
        this.renderTodos();
    }
    
    loadTodos() {
        // 기본 할 일 목록
        this.todos = [
            {
                id: 1,
                text: '김민수 고객 대출',
                completed: false
            },
            {
                id: 2,
                text: '월말 정산 보고서 작성',
                completed: false
            },
            {
                id: 3,
                text: '신규 고객 상담 준비',
                completed: false
            }
        ];
    }
    
    setupEventListeners() {
        // 추가 버튼
        const addBtn = document.getElementById('add-task-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showModal());
        }
        
        // 모달 관련
        const modal = document.getElementById('todo-modal');
        const modalClose = document.getElementById('modal-close');
        const btnCancel = document.getElementById('btn-cancel');
        const btnAdd = document.getElementById('btn-add');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.hideModal());
        }
        
        if (btnCancel) {
            btnCancel.addEventListener('click', () => this.hideModal());
        }
        
        if (btnAdd) {
            btnAdd.addEventListener('click', () => this.addTodo());
        }
        
        // 모달 외부 클릭 시 닫기
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
        
        // Enter 키로 추가
        const taskInput = document.getElementById('new-task-input');
        if (taskInput) {
            taskInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addTodo();
                }
            });
        }
    }
    
    showModal() {
        const modal = document.getElementById('todo-modal');
        const taskInput = document.getElementById('new-task-input');
        
        if (modal) {
            modal.classList.add('show');
            // 포커스
            if (taskInput) {
                setTimeout(() => taskInput.focus(), 100);
            }
        }
    }
    
    hideModal() {
        const modal = document.getElementById('todo-modal');
        const taskInput = document.getElementById('new-task-input');
        
        if (modal) {
            modal.classList.remove('show');
        }
        
        // 입력 필드 초기화
        if (taskInput) {
            taskInput.value = '';
        }
    }
    
    addTodo() {
        const taskInput = document.getElementById('new-task-input');
        
        if (!taskInput) return;
        
        const text = taskInput.value.trim();
        if (!text) {
            alert('할 일을 입력해주세요.');
            return;
        }
        
        const newTodo = {
            id: this.nextId++,
            text: text,
            completed: false
        };
        
        this.todos.push(newTodo);
        this.renderTodos();
        this.hideModal();
    }
    
    
    toggleTodo(id) {
        const todo = this.todos.find(t => t.id === id);
        if (todo) {
            todo.completed = !todo.completed;
            this.renderTodos();
        }
    }
    
    
    deleteTodo(id) {
        if (confirm('정말 삭제하시겠습니까?')) {
            this.todos = this.todos.filter(t => t.id !== id);
            this.renderTodos();
        }
    }
    
    renderTodos() {
        const todoList = document.getElementById('todo-list');
        if (!todoList) return;
        
        todoList.innerHTML = '';
        
        this.todos.forEach(todo => {
            const todoItem = this.createTodoElement(todo);
            todoList.appendChild(todoItem);
        });
    }
    
    createTodoElement(todo) {
        const todoItem = document.createElement('div');
        todoItem.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        todoItem.setAttribute('data-id', todo.id);
        
        todoItem.innerHTML = `
            <div class="todo-checkbox">
                <input type="checkbox" id="todo-${todo.id}" class="todo-check" ${todo.completed ? 'checked' : ''}>
                <label for="todo-${todo.id}" class="todo-check-label"></label>
            </div>
            <div class="todo-content">
                <span class="todo-text">${todo.text}</span>
            </div>
            <div class="todo-actions">
                <button class="todo-delete-btn" data-id="${todo.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        // 이벤트 리스너 추가
        const checkbox = todoItem.querySelector('.todo-check');
        const deleteBtn = todoItem.querySelector('.todo-delete-btn');
        
        if (checkbox) {
            checkbox.addEventListener('change', () => this.toggleTodo(todo.id));
        }
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.deleteTodo(todo.id));
        }
        
        return todoItem;
    }
}


// 페이지 로드 시 위젯 초기화
document.addEventListener('DOMContentLoaded', function() {
    window.todoWidget = new TodoWidget();
});
