import React from 'react';

const Footer = () => {
  return (
    <footer style={styles.footer}>
      <div style={styles.footerColumn}>
        <h4 style={styles.heading}>Explore</h4>
        <ul style={styles.list}>
          <li style={styles.listItem}><a href="#about" style={styles.link}>About Us</a></li>
          <li style={styles.listItem}><a href="#contact" style={styles.link}>Contact</a></li>
          <li style={styles.listItem}><a href="#support" style={styles.link}>Support</a></li>
        </ul>
      </div>
      <div style={styles.footerColumn}>
        <h4 style={styles.heading}>Follow Us</h4>
        <ul style={styles.list}>
          <li style={styles.listItem}><a href="https://twitter.com" style={styles.link}>Twitter</a></li>
          <li style={styles.listItem}><a href="https://instagram.com" style={styles.link}>Instagram</a></li>
        </ul>
      </div>
      <div style={styles.footerColumn}>
        <h4 style={styles.heading}>Legal</h4>
        <ul style={styles.list}>
          <li style={styles.listItem}><a href="#privacy" style={styles.link}>Privacy Policy</a></li>
          <li style={styles.listItem}><a href="#terms" style={styles.link}>Terms of Use</a></li>
        </ul>
      </div>
    </footer>
  );
};

const styles = {
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '20px',
    backgroundColor: '#20A39E', // Teal background
    color: 'white',
    borderTop: '3px solid #EF5B5B', // Vibrant red border
  },
  footerColumn: {
    flex: 1,
    padding: '10px',
  },
  heading: {
    color: '#FFBA49', // Bright yellow for headings
  },
  list: {
    listStyleType: 'none',
    padding: 0,
  },
  listItem: {
    marginBottom: '10px',
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    opacity: 0.8,
    transition: 'opacity 0.3s',
  },
};

export default Footer;
