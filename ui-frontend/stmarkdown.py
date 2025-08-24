def stmarkdown():
    return """
    <style>
    /* Your CSS styles unchanged */
.user-info-logout-container {
    position: fixed;
    top: 15px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    background: #ffffffcc;
    padding: 8px 16px;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(178, 34, 34, 0.4);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 15px;
    user-select: none;
    z-index: 11000;
    white-space: nowrap;
}
.user-info-text {
    color: #222;
    user-select: text;
    line-height: 1.2;
}
.user-info-text b {
    margin-right: 8px;
}
.logout-button {
    background-color: #b22222;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 900;
    font-size: 14px;
    user-select: none;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 10px rgba(178, 34, 34, 0.6);
    white-space: nowrap;
}
.logout-button:hover {
    background-color: #7f1616;
    box-shadow: 0 6px 15px rgba(127, 22, 22, 0.9);
}
.app-content {
    margin-top: 80px;
    margin-left: auto;
    margin-right: auto;
    max-width: 1150px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
[data-baseweb="tab-list"] {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0;
    gap: 16px !important;
    justify-content: center;
}
[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 16px;
    padding: 8px 22px;
    border-radius: 10px;
    border: 2px solid #b22222;
    margin: 0 4px;
    color: #b22222;
    transition: all 0.3s ease;
    background-color: white;
}
[data-baseweb="tab"]:hover {
    background-color: #ffeaea;
    cursor: pointer;
}
[data-baseweb="tab"][aria-selected="true"] {
    background-color: #b22222 !important;
    color: white !important;
    font-weight: bold;
}
.login-form-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 150px;
}
.login-form-container input[type="text"],
.login-form-container input[type="password"] {
    max-width: 100px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
    font-size: 14px !important;
    padding: 6px 10px !important;
    border-radius: 5px !important;
}
.login-box {
    background: white;
    padding: 2rem 3rem;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.05);
    width: 50%;
    max-width: 200px;
    text-align: center;
    margin-top: 80px;
}
.login-form-container {
    margin-top: 0 !important;
    padding-top: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}
.customer-card {
    background: white;
    padding: 2.5rem 3rem;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    max-width: 700px;
    margin: 3rem auto 1rem auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #222;
    line-height: 1.6;
    user-select: text;
}
.customer-header {
    font-weight: 900;
    font-size: 2.2rem;
    color: #b22222;
    margin-bottom: 1.5rem;
}
.customer-card p {
    font-size: 1.1rem;
    margin: 0.5rem 0;
}
.customer-card p strong {
    margin-left: 0.3rem;
    color: #555;
}
.recommendations-section {
    max-width: 700px;
    margin: 1rem auto 3rem auto;
    padding-top: 1.5rem;
    border-top: 3px solid #b22222;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    user-select: text;
    color: #222;
}
.recommendations-section h3 {
    font-weight: 800;
    font-size: 1.7rem;
    color: #b22222;
    margin-bottom: 1rem;
}
.back-button {
    background-color: #b22222;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    color: white;
    font-weight: 700;
    cursor: pointer;
    font-size: 16px;
    margin-top: 0;
    margin-bottom: 4rem;
    display: block;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    user-select: none;
    transition: background-color 0.3s ease;
}
.back-button:hover {
    background-color: #7f1616;
}
.recommendation-card {
    background: #fff0f0;
    padding: 0.8rem 1rem;
    border-radius: 15px;
    margin-bottom: 0.8rem;
    box-shadow: 0 3px 8px rgba(178,34,34,0.12);
    cursor: pointer;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    transition: background-color 0.3s ease;
}
.recommendation-card:hover {
    background-color: #ffeaea;
}
.recommendation-card-expanded {
    background: #fff8f8;
    padding: 1rem 1.2rem;
    border-radius: 15px;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 14px rgba(178,34,34,0.25);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.offer-customer-button-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}
.offer-customer-button {
    background-color: #b22222;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 700;
    font-size: 16px;
    user-select: none;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 10px rgba(178, 34, 34, 0.6);
    white-space: nowrap;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.offer-customer-button:hover {
    background-color: #7f1616;
    box-shadow: 0 6px 15px rgba(127, 22, 22, 0.9);
}
</style>
    """