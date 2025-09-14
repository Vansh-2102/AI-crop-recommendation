import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, MapPin, Phone, Edit, Save, X } from 'lucide-react';
import { toast } from 'react-hot-toast';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    location: user?.location || '',
    farmSize: user?.farmSize || '',
    experience: user?.experience || '',
    crops: user?.crops || []
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleCropChange = (index, value) => {
    const newCrops = [...formData.crops];
    newCrops[index] = value;
    setFormData({
      ...formData,
      crops: newCrops
    });
  };

  const addCrop = () => {
    setFormData({
      ...formData,
      crops: [...formData.crops, '']
    });
  };

  const removeCrop = (index) => {
    const newCrops = formData.crops.filter((_, i) => i !== index);
    setFormData({
      ...formData,
      crops: newCrops
    });
  };

  const handleSave = async () => {
    try {
      await updateProfile(formData);
      toast.success('Profile updated successfully!');
      setIsEditing(false);
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      location: user?.location || '',
      farmSize: user?.farmSize || '',
      experience: user?.experience || '',
      crops: user?.crops || []
    });
    setIsEditing(false);
  };

  return (
    <div className="profile">
      <div className="page-header">
        <h1>Profile</h1>
        <p>Manage your account information and farm details</p>
      </div>

      <div className="profile-container">
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              <User size={48} />
            </div>
            <div className="profile-info">
              <h2>{user?.name || 'Farmer'}</h2>
              <p>{user?.email}</p>
            </div>
            <div className="profile-actions">
              {!isEditing ? (
                <button onClick={() => setIsEditing(true)} className="edit-btn">
                  <Edit size={20} />
                  Edit Profile
                </button>
              ) : (
                <div className="edit-actions">
                  <button onClick={handleSave} className="save-btn">
                    <Save size={20} />
                    Save
                  </button>
                  <button onClick={handleCancel} className="cancel-btn">
                    <X size={20} />
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="profile-details">
            <div className="detail-section">
              <h3>Personal Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>
                    <User size={20} />
                    Full Name
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="Enter your full name"
                    />
                  ) : (
                    <span>{formData.name || 'Not provided'}</span>
                  )}
                </div>

                <div className="detail-item">
                  <label>
                    <Mail size={20} />
                    Email
                  </label>
                  {isEditing ? (
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="Enter your email"
                    />
                  ) : (
                    <span>{formData.email}</span>
                  )}
                </div>

                <div className="detail-item">
                  <label>
                    <Phone size={20} />
                    Phone
                  </label>
                  {isEditing ? (
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="Enter your phone number"
                    />
                  ) : (
                    <span>{formData.phone || 'Not provided'}</span>
                  )}
                </div>

                <div className="detail-item">
                  <label>
                    <MapPin size={20} />
                    Location
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      placeholder="Enter your location"
                    />
                  ) : (
                    <span>{formData.location || 'Not provided'}</span>
                  )}
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>Farm Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Farm Size (acres)</label>
                  {isEditing ? (
                    <input
                      type="number"
                      name="farmSize"
                      value={formData.farmSize}
                      onChange={handleChange}
                      placeholder="Enter farm size"
                    />
                  ) : (
                    <span>{formData.farmSize || 'Not provided'}</span>
                  )}
                </div>

                <div className="detail-item">
                  <label>Farming Experience (years)</label>
                  {isEditing ? (
                    <input
                      type="number"
                      name="experience"
                      value={formData.experience}
                      onChange={handleChange}
                      placeholder="Enter years of experience"
                    />
                  ) : (
                    <span>{formData.experience || 'Not provided'}</span>
                  )}
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>Crops Grown</h3>
              {isEditing ? (
                <div className="crops-editor">
                  {formData.crops.map((crop, index) => (
                    <div key={index} className="crop-input">
                      <input
                        type="text"
                        value={crop}
                        onChange={(e) => handleCropChange(index, e.target.value)}
                        placeholder="Enter crop name"
                      />
                      <button
                        type="button"
                        onClick={() => removeCrop(index)}
                        className="remove-crop-btn"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                  <button onClick={addCrop} className="add-crop-btn">
                    Add Crop
                  </button>
                </div>
              ) : (
                <div className="crops-list">
                  {formData.crops.length > 0 ? (
                    formData.crops.map((crop, index) => (
                      <span key={index} className="crop-tag">
                        {crop}
                      </span>
                    ))
                  ) : (
                    <span className="no-crops">No crops added yet</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="profile-stats">
          <h2>Farm Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Crops</h3>
              <p>{formData.crops.length}</p>
            </div>
            <div className="stat-card">
              <h3>Farm Size</h3>
              <p>{formData.farmSize || '0'} acres</p>
            </div>
            <div className="stat-card">
              <h3>Experience</h3>
              <p>{formData.experience || '0'} years</p>
            </div>
            <div className="stat-card">
              <h3>Member Since</h3>
              <p>2024</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
