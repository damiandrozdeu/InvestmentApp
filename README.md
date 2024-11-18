
# **Stock Portfolio Simulator**

## **Overview**
Stock Portfolio Simulator is a web application designed to provide users with a platform to simulate stock market investments. Users can manage a portfolio by buying and selling stocks, monitor price trends, and track their balance and transactions in real time. The platform also includes advanced features such as setting target prices for automatic sell orders and maintaining a list of favorite stocks.

## **Distinctiveness and Complexity**
This project is distinct and complex due to the following reasons:
1. **Unique Functionality**: Unlike traditional e-commerce or social networking platforms, this project is focused on simulating the stock market. It allows users to interact with live market data, manage financial transactions, and utilize tools like pending sell orders.
2. **Dynamic Features**: Includes real-time data updates via integration with the `yfinance` API, interactive charts powered by Chart.js, and responsive modals for stock transactions.
3. **Data-Driven Architecture**: The project employs a relational database to manage stocks, user portfolios, transactions, and historical data. Each component interacts dynamically with others, creating a complex yet intuitive user experience.
4. **Admin Features**: Administrators can update stock prices and manage the backend effectively, adding another layer of complexity and control.
5. **Responsive Design**: The application is fully mobile-responsive, ensuring usability across devices.

## **Key Features**
- **Portfolio Management**: View holdings, balance, and transaction history.
- **Market Overview**: Browse stocks with search and filter options, view price trends, and purchase shares.
- **Dynamic Transactions**: Buy, sell, and set target prices for stocks.
- **Favorites Management**: Mark stocks as favorites for quick access.
- **Admin Controls**: Update stock prices and manage historical data.

## **File Structure**
- **`simulator/`**:
  - `models.py`: Defines models for `UserProfile`, `Stock`, `Transaction`, `PendingSell`, `Favorite`, and `StockHistory`.
  - `views.py`: Contains all backend logic, including views for portfolio, market, stock transactions, and admin features.
  - `urls.py`: Maps URLs to corresponding views.
- **`templates/simulator/`**:
  - `base.html`: Base template for consistent layout.
  - `portfolio.html`: Displays user portfolio, transactions, and fund management options.
  - `market.html`: Lists stocks with filtering and search options.
  - `favorites.html`: Shows a user's favorite stocks.
- **`static/js/`**:
  - `portfolio.js`: Handles modals and AJAX calls for portfolio-related actions.
  - `market.js`: Updates the stock table dynamically and fetches stock details.
- **`static/css/`**:
  - Contains custom styles for improving the UI/UX.
- **`requirements.txt`**: Lists dependencies such as `Django`, `yfinance`, and `Chart.js`.

## **How to Run**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/stock-portfolio-simulator.git
   cd stock-portfolio-simulator
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Run the Server**:
   ```bash
   python manage.py runserver
   ```
5. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

## **Key Dependencies**
- **Django**: Backend framework for managing models, views, and templates.
- **yfinance**: Fetching real-time stock data.
- **Chart.js**: Interactive charts for stock price history.
- **Bootstrap**: Ensuring responsive design.

## **Future Enhancements**
- **Live Market Updates**: Integrate WebSocket for real-time price changes.
- **Comprehensive Analytics**: Provide insights on portfolio performance over time.
- **User Education**: Add tutorials or guides on investing in stocks.
